#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source
from scrapers import ScraperHypar
import re
import time

epochDate = date(2007, 11, 13) # = 835277... okay it's not really an "epoch"

startDate = date(2007, 11, 28)
endDate = date(2007, 11, 30) #scraper is inclusive of both dates

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
				
def dateToNum(date):
	return 835277 + (date - epochDate).days

def populateArticlesList(conn):
	startNum = dateToNum(startDate)
	endNum = dateToNum(endDate)
	i = startNum
	while i <= endNum:
		url = urlTemplate % i
		articlesHtml = getPage(conn, url)
		articleTags = articlesHtml.find_class("local_news")
		dateTags = articlesHtml.find_class("local_news_smp")
		for j in range(0, len(articleTags)):
			aTag = articleTags[j]
			dateTag = dateTags[j]
			url = re.sub(r'\?id=.*','',aTag.attrib["href"])
			title = (aTag.text).strip()
			date = re.findall('[0-9]{2}\.[0-9]{2}\.[0-9]{4}', (dateTag.text).strip())[0]
			date = time.strftime('%Y-%m-%d', time.strptime(date, "%d.%m.%Y"))
			articles.append((title, url, date))
		i += 1
	
def main(startDate, endDate):
	print("Getting URLs from %s to %s..." % (startDate, endDate)) #inclusive of both dates
	conn = http.client.HTTPConnection("www.hypar.ru")
	populateArticlesList(conn)
	print("%s URLs scraped from %s to %s" % (str(len(articles)), startDate, endDate))
	print("Scraping article content...")
	ids = None
	root = None
	scrapedNum = 0
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
	print("%s articles scraped" % scrapedNum)
	conn.close()

main(startDate, endDate)