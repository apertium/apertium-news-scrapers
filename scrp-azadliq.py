#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source
from scrapers import ScraperAzadliq
import copy

startDate = date(2012, 12, 1)
endDate = date(2012, 12, 10) #scraper is inclusive of both dates
numPages = 10 #number of pages to scrape in the categories

urlTemplate = '/archive/news/%s/1/1.html'
categoryUrlTemplates = ['/archive/az_politics/%s/3/3.html', '/archive/az_society/%s/2/2.html', '/archive/az_economy/%s/4/4.html', '/archive/az_world/%s/749/749.html', '/archive/sport/%s/3577/3577.html']

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
			aTag = liTag[1]
			url = aTag.attrib["href"]
			if len(aTag) is 2:
				spanTag = aTag[1]
				title = (spanTag.text).strip()
			else:
				title = title = (aTag.text).strip()
			articles.append((title, "http://www.azadliq.org" + url, tempDate))
		tempDate = tempDate + oneDay
		
	for pageNum in range(1, numPages):
		for categoryUrlTemplate in categoryUrlTemplates:
			url = categoryUrlTemplate % pageNum
			rawArticlesHtml = getPage(conn, url, rawContent = True).split("pages -->")[1]
			articlesHtml = lxml.html.fromstring(rawArticlesHtml)
			
			if('az_society' in categoryUrlTemplate or 'az_politics' in categoryUrlTemplate):
				articleTags = articlesHtml.xpath("descendant-or-self::*[contains(concat(' ', normalize-space(@class), ' '), ' archive_rowmm ')]/descendant::*[contains(concat(' ', normalize-space(@class), ' '), ' black ')]")
				if len(articleTags) is 0:
					print('Stopped scraping category %s after %s pages' % (url, pageNum))
					continue
				for hTag in articleTags:
					aTag = hTag[0]
					url = aTag.attrib["href"]
					if len(aTag) is 2:
						spanTag = aTag[1]
						title = (spanTag.text).strip()
					else:
						title = title = (aTag.text).strip()
					articles.append((title, "http://www.azadliq.org" + url, tempDate))
				
			elif('az_world' in categoryUrlTemplate or 'az_economy' in categoryUrlTemplate or 'sport' in categoryUrlTemplate):
				articleTags = articlesHtml.find_class("zoomMe")
				if len(articleTags) is 0:
					print('Stopped scraping category %s after %s pages' % (url, pageNum))
					continue
				for liTag in articleTags:
					if not len(liTag):
						continue #some extraneous elements are being captured
					aTag = liTag[0]
					url = aTag.attrib["href"]
					if len(aTag) is 2:
						spanTag = aTag[1]
						title = (spanTag.text).strip()
					else:
						title = title = (aTag.text).strip()
					articles.append((title, "http://www.azadliq.org" + url, tempDate))
					
			else:
				pass

def main(startDate, endDate):
	print("Getting URLs from %s to %s and from %s pages..." % (startDate, endDate, numPages))
	conn = http.client.HTTPConnection("www.azadliq.org")
	populateArticlesList(conn)
	#printArticles(articles, 'test2.txt', False)
	print("%s URLs scraped from %s to %s and from %s pages" % (str(len(articles)), startDate, endDate, numPages))
	print("Scraping article content...")
	ids = None
	root = None
	scrapedNum = 0
	for (title, url, date) in articles:
		try:
			source = Source(url, title=title, date = date, scraper=ScraperAzadliq, conn=conn)
			source.makeRoot("./", ids=ids, root=root, lang="aze")
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