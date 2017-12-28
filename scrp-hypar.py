#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source, Writer
from scrapers import ScraperHypar
import re
import time
import copy
import calendar
import signal
import sys

startDate = date(2012, 1, 1)
endDate = date(2012, 12, 31) #scraper is inclusive of both dates

urlTemplate = "/nws/cldr/32/%s/index.php"

articles = []

def getPage(conn, url, rawContent = False):
	conn.request("GET", url)
	res = conn.getresponse()
	if res.status != 200:
		print(url, res.status, res.reason)
		return
	contents = res.read().decode('cp1251').encode('utf8').decode('utf-8')
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
				file.write("%s, %s, %s\n" % (title, url, str(date)))
				
def dateToNum(convertDate):
	yearDates = {2007 : (date(2007, 11, 13), 835277),
				 2008 : (date(2008, 1, 10), 835370), 
				 2009 : (date(2009, 1, 11), 835787),
				 2010 : (date(2010, 1, 12), 836204),
				 2011 : (date(2011, 1, 12), 836620),
				 2012 : (date(2012, 1, 11), 837035)
				 }
	daysMonth = [0, 31, -1, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	daysInMonth = 32
	daysMonth[2] = 29 if calendar.isleap(convertDate.year) else 28
	num = yearDates[convertDate.year][1] + (convertDate - yearDates[convertDate.year][0]).days
	for i in range(1, convertDate.month):
		num += daysInMonth - daysMonth[i]
	return num

def populateArticlesList(conn):
	oneDay = timedelta(days = 1)
	tempDate = copy.deepcopy(startDate)
	while tempDate <= endDate:
		dayNum = dateToNum(tempDate)
		url = urlTemplate % dayNum
		articlesHtml = getPage(conn, url)
		articleTags = articlesHtml.find_class("local_news")
		dateTags = articlesHtml.find_class("local_news_smp")
		for i in range(0, len(articleTags)):
			aTag = articleTags[i]
			dateTag = dateTags[i]
			url = re.sub(r'\?id=.*','',aTag.attrib["href"])
			title = (aTag.text).strip()
			date = re.findall('[0-9]{2}\.[0-9]{2}\.[0-9]{4}', (dateTag.text).strip())[0]
			date = time.strftime('%Y-%m-%d', time.strptime(date, "%d.%m.%Y"))
			articles.append((title, url, date))
		tempDate += oneDay
	
def main(startDate, endDate):
	print("Getting URLs from %s to %s..." % (startDate, endDate)) #inclusive of both dates
	conn = http.client.HTTPConnection("www.hypar.ru")
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
				source = Source(url, title=title, date = date, scraper=ScraperHypar, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang="cv")
				source.add_to_archive()
				if ids is None:
					ids = source.ids
				if root is None:
					root = source.root
				scrapedNum += 1
			except Exception as e:
				print(url + " " + str(e))			
	except KeyboardInterrupt:
		print("\nReceived a keyboard interrupt. Closing the program.")
	print("%s articles scraped" % scrapedNum)
	w.close()
	conn.close()

main(startDate, endDate)
