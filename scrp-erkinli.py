#!/usr/bin/env python3

from datetime import date,timedelta
import lxml.html
import http.client
from scraper_classes import Source, Writer
from scrapers import ScraperAzadliq
import copy
import signal
import sys

startDate = date(2013, 1, 1) #dates to scrape in the sections with calendar
endDate = date(2013, 12, 31) #scraper is inclusive of both dates
numPages = 60 #number of pages to scrape in the categories, scrape from 1 (newest) to numPages (oldest)

urlTemplate = '/archive/%s/%s/%s/%s.html'
urlStructures = [('news', '16090', 'cal'),
				('dagestan', '16094', 'cat'),
				('politics', '16126', 'cat'),
				('human_rights', '16097', 'cat'),
				('religion', '16127', 'cat'),
				('interview_', '16129', 'cat'),
				('russia', '16095', 'cat'),
				('world', '16098', 'cal'),
				('north_caucasus', '16099', 'cat'),
				('art_culture', '16100', 'cal'),
				('economy', '16101', 'cal'),
				('history', '16102', 'cat'),
				('announcement', '16103', 'cal'),
				('avar_language', '16104', 'cat'),
				('russia_diary', '16106', 'cat'),
				('my_rights_my_freedom', '16107', 'cat'),
				('analysis_commentary', '16092', 'cat'),
				('caucasus', '16105', 'cal'),
				('caucasus_compass', '16108', 'cat'),
				('world_and_religions', '16109', 'cat'),
				('literature', '16128', 'cat'),
				('nature', '16130', 'cat'),
				('hearth', '16105', 'cat'),
				('sport', '16149', 'cat'),
				('family', '16150', 'cal'),
				('question-of-the-week', '16618', 'cat'),
				('history-by-names', '16741', 'cat'),
				('interview_', '16129', 'cat')]

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
	scrapedCategories = []
	for urlStructure in urlStructures:
		if urlStructure[2] == 'cal':
			oneDay = timedelta(days = 1)
			tempDate = copy.deepcopy(startDate)
			while tempDate <= endDate:
				url = urlTemplate % (urlStructure[0], tempDate.isoformat().replace('-',''), urlStructure[1], urlStructure[1])
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
		elif urlStructure[2] == 'cat':
			for pageNum in range(0, numPages):
				if not urlStructure[0] in scrapedCategories: #only if scraping not complete
					url = urlTemplate % (urlStructure[0], pageNum, urlStructure[1], urlStructure[1])
					rawArticlesHtml = getPage(conn, url, rawContent = True).split("pages -->")[1]
					articlesHtml = lxml.html.fromstring(rawArticlesHtml)
					if('az_society' == urlStructure[0] or 'az_politics' == urlStructure[0]):
						articleTags = articlesHtml.xpath("descendant-or-self::*[contains(concat(' ', normalize-space(@class), ' '), ' archive_rowmm ')]/descendant::*[contains(concat(' ', normalize-space(@class), ' '), ' black ')]")
						if len(articleTags) is 0:
							print('Stopped scraping category %s after %s pages' % (urlStructure[0], pageNum))
							scrapedCategories.append(urlStructure[0]) #scraping complete
						for hTag in articleTags:
							aTag = hTag[0]
							url = aTag.attrib["href"]
							if len(aTag) is 2:
								spanTag = aTag[1]
								title = (spanTag.text).strip()
							else:
								title = title = (aTag.text).strip()
							articles.append((title, "http://www.azadliq.org" + url, tempDate))
					elif('az_world' == urlStructure[0] or 'az_economy' == urlStructure[0] or 'sport' == urlStructure[0]):
						articleTags = articlesHtml.find_class("zoomMe")
						if len(articleTags) is 0:
							print('Stopped scraping category %s after %s pages' % (urlStructure[0], pageNum))
							scrapedCategories.append(urlStructure[0]) #scraping complete
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
		print('Scraping %s complete, current article URLs scraped: %s' % (urlStructure[0], str(len(articles))))


def main(startDate, endDate):
	print("Getting URLs from %s to %s and from %s pages..." % (startDate, endDate, numPages))
	conn = http.client.HTTPConnection("www.radioerkinli.com")
	populateArticlesList(conn)
	#printArticles(articles, 'test2.txt', False)
	print("%s URLs scraped from %s to %s and from %s pages * %s categories" % (str(len(articles)), startDate, endDate, numPages, str(len(urlStructures)-1)))
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
				source = Source(url, title=title, date=date, scraper=ScraperAzadliq, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang="ava")
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
