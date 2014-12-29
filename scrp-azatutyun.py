#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source, Writer
from scrapers import ScraperAzatutyun
import copy
import signal
import sys

startDate = date(2012, 12, 1)
endDate = date(2012, 12, 31) #scraper is inclusive of both dates

urlTemplate = "/archive/Armenian_Archive/%s/729/729.html"

articles = []

def getPage(conn, url, rawContent = False):
	conn.request("GET", url)
	res = conn.getresponse()
	if res.status != 200:
		print(url, res.status, res.reason)
		return
	contents = res.read().decode('utf-8')
	if rawContent:
		return contents
	doc = lxml.html.fromstring(contents)
	return doc

def printArticles(articlesData, fileName, display=False):
	if display:
		for (title, url, date) in articlesData:
			print(title, url, date.isoformat())
	else:
		with open(fileName, 'a', encoding='utf-8') as file:
			for (title, url, date) in articlesData:
				file.write("%s, %s, %s\n" % (title, url, date.isoformat()))

def populateArticlesList(conn):
	oneDay = timedelta(days = 1)
	tempDate = copy.deepcopy(startDate)
	while tempDate <= endDate:
		url = urlTemplate % tempDate.isoformat().replace('-','')
		rawArticlesHtml = getPage(conn, url, rawContent = True).split("pages -->")[1]
		articlesHtml = lxml.html.fromstring(rawArticlesHtml)
		articleTags = articlesHtml.find_class("zoomMe")
		for liTag in articleTags:
			aTag = liTag[0]
			url = aTag.attrib["href"]
			if len(aTag) is 2:
				spanTag = aTag[1]
				title = (spanTag.text).strip()
			else:
				title = title = (aTag.text).strip()
			articles.append((title, "http://www.azatutyun.am" + url, tempDate))
		tempDate = tempDate + oneDay
	
def main(startDate, endDate):
	print("Getting URLs from %s to %s..." % (startDate, endDate)) #inclusive of both dates
	conn = http.client.HTTPConnection("www.azatutyun.am")
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
		for (title, url, date) in articles:
			try:
				source = Source(url, title=title, date = date, scraper=ScraperAzatutyun, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang="hye")
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

fileName = 'test2.txt'
with open(fileName, 'w'):
    pass
main(startDate, endDate)
