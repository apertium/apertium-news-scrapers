#!/usr/bin/env python3

from datetime import date, timedelta
from urllib import request
#from lxml import etree
import lxml.html
import lxml.html.clean
from scrapers import ScraperAzathabar
from scraper_classes import Source, Writer
import urllib.error
import http.client
import curses
import sys
import signal

domain = "www.azathabar.com"
urltemplate = "/archive/%s/%s%02d%02d/%s/%s.html"

topics = { 2239: ("news", "day"),
	2246: ("Turkmenistan", "days"),
	2247: ("asia", "days"),
	2248: ("international", "days"),
	2275: ("special_programs", "days"),
	2289: ("Multimedia", "days"),
	2756: ("Blogs", "days"),
	#2240: ("commentary", "month"),
	#2244: ("interview", "month"),
	2241: ("politics", "days"),
	2242: ("economics", "days"),
	2243: ("society", "days"),
	#2245: ("culture", "month"),
	#2800: ("History", "year"),
	#2276: ("newscast", "month"),
	#2249: ("analytical", "month"),
	2250: ("neighbors", "days"),
	#2251: ("style", "month"),
	#2252: ("youth", "month"),
	#2253: ("economy", "month"),
	2254: ("spotlight", "days"),
	#2255: ("women", "month"),
	#2256: ("rights", "month"),
	2257: ("health", "days"),
	2258: ("time", "days"),
	#2259: ("review", "month"),
	#2261: ("music", "month"),
	#2263: ("personalities", "month"),
	#2984: ("No_Comment", "??"),
	3264: ("Voice_of_people", "days"),
}	

startyear = 2010
endyear = 2010
minmonth = 1
maxmonth = 12

startnum = 1

def get_urls(monthurl, pagetype):  # get the URLS for a given month
	global domain
	sys.stdout.write("\rGetting %s." % monthurl)
	sys.stdout.flush()

	conn = http.client.HTTPConnection(domain)
	conn.request("GET", monthurl)
	res = conn.getresponse()
	if res.status != 200:
		print(monthurl, res.status, res.reason)
		return
	contents = res.read().decode('utf-8')
	sys.stdout.write(".")
	sys.stdout.flush()

	doc = lxml.html.fromstring(contents)
	mid = doc.find_class("middlePart")[0]

	curdate = ""
	urls = []
	for el in mid.findall(".//li"):
		#if "class" in el.attrib:
		#	if "archive_listrow_date" in el.attrib['class'].split():
		#		curdate = el.text
		#if curdate != "":
		if "class" in el.attrib:
			classes = el.attrib['class'].split()
			if pagetype == "days":
				if "archive_listrow_date" in classes:
					curdate = el.text
			#if "archive_listrow_date" in el.attrib['class'].split():
			#	curdate = el.text
			#if curdate != "":
			#	elif "zoomMe" in classes and "date" not in classes:
			if "zoomMe" in classes and "date" not in classes:
				title = None
				url = None
				for a in el.findall(".//a"):
					if "style" not in a.attrib:
						title = a.text
						url = a.attrib["href"]
				if title == None or url == None:
					for a in el.findall(".//a"):
						title = a.text
						url = a.attrib["href"]
					#print(lxml.html.tostring(el)) #lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8'))))
				if title != None and url != None:
					urls.append((url, title))
					#print(url, title)
	sys.stdout.write("%s urls" % len(urls))
	
	sys.stdout.write(".\n")
	sys.stdout.flush()
	conn.close()
	return urls

def get_allurls(startyear, endyear, minmonth, maxmonth):  # get all urls for given date range
	allurls = []

	for year in range(startyear, endyear+1):
		for month in range(minmonth, maxmonth+1):
			for num, (topic, pagetype) in topics.items():
				if pagetype=="day":
					for day in range(1, 32):
						dayurl = urltemplate % (topic, year, month, day, num, num)
						urls = get_urls(dayurl, pagetype)

						if urls is not None:
							for url in urls:
								allurls.append(url)
				elif pagetype=="days":
					dayurl = urltemplate % (topic, year, month, 1, num, num)
					urls = get_urls(dayurl, pagetype)

					if urls is not None:
						for url in urls:
							allurls.append(url)
				
	
	return allurls


def main():
	global startyear, endyear, minmonth, maxmonth, domain

	sys.stdout.write("\rGenerating urls...\n")
	sys.stdout.flush()
	allurls = get_allurls(startyear, endyear, minmonth, maxmonth)

	sys.stdout.write("\r%d articles total\n" % len(allurls))

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
		for (url, title) in allurls:
			#sys.stdout.write("\r"+url+" "+title+"\n")
			#sys.stdout.flush()
			this += 1
			try:
				source = Source(url, title=title, scraper=ScraperAzathabar, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang="tuk")
				msg = "(%s/%s)" % (this, len(allurls))
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

def tryOneArticle(url):
	global domain
	root = None
	ids = None
	conn = http.client.HTTPConnection(domain)
	w  = Writer()
	source = Source(url, title="", scraper=ScraperAzathabar, conn=conn)
	source.makeRoot("./", ids=ids, root=root, lang="tuk")
	source.add_to_archive()
	w.close()
	conn.close()

main()
#tryOneArticle("http://www.azathabar.com/archive/news/20111231/2239/2239.html?id=24439101")
#tryOneArticle("http://www.azathabar.com/content/article/24437444.html")
#tryOneArticle("http://www.azathabar.com/content/article/24425908.html")
#tryOneArticle("http://www.azathabar.com//content/article/2306850.html")
