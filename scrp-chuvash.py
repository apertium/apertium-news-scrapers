#!/usr/bin/env python3

from datetime import date
import time
import lxml.html
import http.client
from scraper_classes import Source
from scrapers import ScraperChuvash
import re

numScrape = 50 #-1 will scrape all articles, 10 will scrape 10 newest articles

urlTemplate = "/news/%s.html"

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

def main(numScrape):
	conn = http.client.HTTPConnection("www.chuvash.org")
	mainPage = getPage(conn, '')
	latestArticleNum = int(mainPage.xpath("//h2[@class='hipar_head']")[0][0].attrib['href'].split('news/')[1].replace('.html',''))
	print('Scraping %s articles...' % ('all' if numScrape is -1 else numScrape))
	numScraped = 0
	attemptScrape = 0
	i = latestArticleNum
	ids = None
	root = None
	while i >= 1 and (numScraped < numScrape or numScrape is -1):
		try:
			url = "http://www.chuvash.org" + (urlTemplate % i)
			source = Source(url, scraper=ScraperChuvash, conn=conn)
			source.makeRoot("./", ids=ids, root=root, lang="cv")
			source.add_to_archive()
			if ids is None:
				ids = source.ids
			if root is None:
				root = source.root
			attemptScrape += 1
			numScraped += 1
			if len(source.out_content) is 0:
				numScraped -= 1
		except Exception as e:
			print(url + " " + str(e))
		i -= 1
	print("Attempted to scrape %s articles." % attemptScrape)	
	print("%s articles scraped." % numScraped)
	conn.close()
	
main(numScrape)



