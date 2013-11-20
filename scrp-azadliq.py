#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source
from scrapers import ScraperAzadliq
import copy

startDate = date(2012, 12, 1) #dates to scrape in the sections with calendar
endDate = date(2012, 12, 1) #scraper is inclusive of both dates
numPages = 15 #number of pages to scrape in the categories, scrape from 1 (newest) to numPages (oldest)

urlTemplates = [('news', '/archive/news/%s/1/1.html', 'cal', False),
				('politics', '/archive/az_politics/%s/3/3.html', 'cat', False),
				('society', '/archive/az_society/%s/2/2.html', 'cat', False),
				('economy', '/archive/az_economy/%s/4/4.html', 'cat', False),
				('world', '/archive/az_world/%s/749/749.html', 'cat', False),
				('sport', '/archive/sport/%s/3577/3577.html', 'cat', False)]

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
	for urlTemplate in urlTemplates:
		if urlTemplate[2] == 'cal':
			oneDay = timedelta(days = 1)
			tempDate = copy.deepcopy(startDate)
			while tempDate <= endDate:
				url = urlTemplate[1] % tempDate.isoformat().replace('-','')
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
		elif urlTemplate[2] == 'cat':
			for pageNum in range(0, numPages):
				if not urlTemplate[3]: #only if scraping not complete
					url = urlTemplate[1] % pageNum
					rawArticlesHtml = getPage(conn, url, rawContent = True).split("pages -->")[1]
					articlesHtml = lxml.html.fromstring(rawArticlesHtml)
					if('society' == urlTemplate[0] or 'politics' == urlTemplate[0]):
						articleTags = articlesHtml.xpath("descendant-or-self::*[contains(concat(' ', normalize-space(@class), ' '), ' archive_rowmm ')]/descendant::*[contains(concat(' ', normalize-space(@class), ' '), ' black ')]")
						if len(articleTags) is 0:
							print('Stopped scraping category %s after %s pages' % (urlTemplate[0], pageNum))
							urlTemplate = urlTemplate[:-1] + (True,) #scraping complete
						for hTag in articleTags:
							aTag = hTag[0]
							url = aTag.attrib["href"]
							if len(aTag) is 2:
								spanTag = aTag[1]
								title = (spanTag.text).strip()
							else:
								title = title = (aTag.text).strip()
							articles.append((title, "http://www.azadliq.org" + url, tempDate))
					elif('world' == urlTemplate[0] or 'economy' == urlTemplate[0] or 'sport' == urlTemplate[0]):
						articleTags = articlesHtml.find_class("zoomMe")
						if len(articleTags) is 0:
							print('Stopped scraping category %s after %s pages' % (urlTemplate[0], pageNum))
							urlTemplate = urlTemplate[:-1] + (True,) #scraping complete
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
		print('Scraping %s complete, current article URLs scraped: %s' % (urlTemplate[0], str(len(articles))))

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
			source = Source(url, title=title, date=date, scraper=ScraperAzadliq, conn=conn)
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