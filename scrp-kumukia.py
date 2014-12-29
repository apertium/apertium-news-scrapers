#!/usr/bin/env python3

import requests, lxml, lxml.html

from urllib import request
import urllib.error
import http.client
import sys
import signal

from scrapers import ScraperAKumukia
from scraper_classes import Source, Writer


debug = False

domain = "kumukia.ru"
siteScraper = ScraperAKumukia
siteLang = "kum"



def _url(path):
	return "http://kumukia.ru/{}".format(path)

def findCats():
	cats = [_url("cat-qumuq.html")]
	links = []
	for cat in cats:

		page = lxml.html.fromstring(requests.get(cat).text)

		sub_page = page.find(".//div[@id='list-subs']")
		if sub_page is not None:
			for sub in sub_page.findall(".//a"):
				for k, v in sub.items():
					if k == "href" and v.startswith("cat-"):
						if _url(v) not in cats:
							cats.append(_url(v))

		for link in page.findall(".//a"):
			if "title" in link.keys():
				title = link.get("title")
				if title == "–>":
					cats.append(_url(link.get("href")))
			if link.text_content() == "Далее...":
				links.append(_url(link.values()[0]))

	if debug:
		for link in links:
			page = requests.get(link)
			if page.status_code != 200:
				print("{} is not reachable...".format(link))

	links = list(set(links))
	print("Found {} articles...".format(len(links)))

	return links



if __name__ == "__main__":

	links = findCats()
	# for testing:
	#links=["http://kumukia.ru/къумукъланы-тарихи-гелиши-ва-адабиятыны-оьсюв-девюрлери.html", "http://kumukia.ru/article-63.html", "http://kumukia.ru/article-9420.html", "http://kumukia.ru/article-9371.html", "http://kumukia.ru/xonshum-inanmasa-da.html"]
	#print("\n".join(links))


	conn = http.client.HTTPConnection(domain)
	ids = None
	root = None
	this = 0
	w = Writer()
	
	def term_handler(sigNum, frame):
		print("\nReceived a SIGTERM signal. Closing the program.")
		w.close()
		sys.exit(0)

	signal.signal(signal.SIGTERM, term_handler)
	
	try:
		#for (url, title) in allurls:
		for link in links:
			#sys.stdout.write("\r"+url+" "+title+"\n")
			#sys.stdout.flush()
			this += 1
			try:
				linkies = link.split('.')
				url = linkies[0]+"."+urllib.parse.quote(linkies[1], encoding="utf8")
				#print(url)
				source = Source(url, scraper=siteScraper, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang=siteLang)
				msg = "(%s/%s)" % (this, len(links))
				source.add_to_archive(msg=msg)
				if ids is None:   # if not ids:
					ids = source.ids
				if root is None:  # if not root:
					root = source.root
			except Exception as e:
				sys.stdout.write(" — %s \n" % e)
				sys.stdout.flush()
				raise
	except KeyboardInterrupt:
		print("\nReceived a keyboard interrupt. Closing the program.")
	w.close()
	conn.close()

