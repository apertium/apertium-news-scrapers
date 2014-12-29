#!/usr/bin/env python3

from datetime import date
import lxml.html
import http.client
from scraper_classes import Source, Writer
from scrapers import ScraperNewsmn
import signal
import sys

startDate = date(2011, 11, 1)
endDate = date(2011, 11, 2) #scraper is inclusive of startDate but does not include endDate

urlTemplate = "/archive.shtml?q=&from=%s&to=%s&sortBy=NEWEST&page=%s"

articles = []

def getPage(conn, url):
	conn.request("GET", url)
	res = conn.getresponse()
	if res.status != 200:
		print(url, res.status, res.reason)
		return
	contents = res.read().decode('utf-8')
	doc = lxml.html.fromstring(contents)
	return doc

def printArticles(articlesData, fileName, display=False):
	if display:
		for (title, url) in articlesData:
			print(title, url)
	else:
		with open(fileName, 'a', encoding='utf-8') as file:
			for (title, url) in articlesData:
				file.write("%s, %s\n" % (title, url))

def populateArticlesList(conn):
	url = urlTemplate % (startDate.isoformat(), endDate.isoformat(),1)
	doc = getPage(conn, url)
	numTag = str(lxml.html.tostring(doc.find_class("search-result")[0]))
	numArticles = int(numTag[numTag.find('/')+2 : numTag.find("</")])
    
	for i in range(1,int(numArticles/20)+2):
		url = urlTemplate % (startDate.isoformat(), endDate.isoformat(),i)
		doc = getPage(conn, url)
		titleTags = doc.find_class("bd-list-title")
		if len(titleTags) is 0:
			break
		for titleTag in titleTags:
			for article in titleTag:
				title = (article.text).strip()
				url = article.attrib["href"]
				articles.append((title, url))
	
def main(startDate, endDate):
	print("Getting URLs from %s to %s..." % (startDate, endDate)) #inclusive of startDate but does not include endDate
	conn = http.client.HTTPConnection("archive.news.mn")
	populateArticlesList(conn)
	print("%s URLs scraped from %s to %s" % (str(len(articles)), startDate, endDate))
	print("Scraping article content...")
	ids = None
	root = None
	scrapedNum = 0
	w = Writer()

	def term_handler(sigNum, frame):
		print("\nReceived a SIGTERM signal. Closing the program.")
		w.close()
		sys.exit(0)

	signal.signal(signal.SIGTERM, term_handler)

	try:
		for (title, url) in articles:
			if url.find("video.news") + url.find("id.news") + url.find("english.news") + url.find("photoalbum") is -4:
				try:
					source = Source(url, title=title, scraper=ScraperNewsmn, conn=conn)
					source.makeRoot("./", ids=ids, root=root, lang="khk")
					source.add_to_archive()
					if ids is None:
						ids = source.ids
					if root is None:
						root = source.root
					scrapedNum += 1
				except Exception as e:
					print(url + " " + str(e))			
		print("%s articles scraped" % scrapedNum)
	
	except KeyboardInterrupt:
		print("\nReceived a keyboard interrupt. Closing the program.")
	w.close()
	conn.close()

fileName = 'test.txt'
with open(fileName, 'w'):
    pass
main(startDate, endDate)
printArticles(articles, fileName) #, display=True)
