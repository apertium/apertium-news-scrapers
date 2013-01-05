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
			print(title, url, str(date))
	else:
		with open(fileName, 'a', encoding='utf-8') as file:
			for (title, url, date) in articlesData:
				file.write("%s, %s, %s\n" % (title, url, str(date)))

def main(numScrape):
	conn = http.client.HTTPConnection("www.chuvash.org")
	mainPage = getPage(conn, '')
	latestArticleNum = int(mainPage.xpath("//h2[@class='hipar_head']")[0][0].attrib['href'].split('news/')[1].replace('.html',''))
	print('Getting %s URLs...' % ('all' if numScrape is -1 else numScrape))
	numScraped = 0 #URLs Scraped
	i = latestArticleNum
	while i >= 1 and (numScraped < numScrape or numScrape is -1):
		url = urlTemplate % i
		articleHtml = getPage(conn, url)
		title = ""
		articlePage = getPage(conn, urlTemplate % i)
		if lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(articlePage.find_class("hipar_text")[0]).decode('utf-8'))).text_content().strip() is not "":
			title = articlePage.xpath("//span[@style='color:#af2900;']")[0].text_content()
			try:
				date = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(articlePage.find_class("tags")[0]).decode('utf-8'))).text_content().strip()
				date = re.findall('[0-9]{2}\.[0-9]{2}\.[0-9]{4}', date)[0]
				date = time.strftime('%d-%m-%Y', time.strptime(date, "%d.%m.%Y"))
			except:
				date = None
			articles.append((title, "http://www.chuvash.org" + url, date))
			numScraped += 1
		i -= 1
	print('%s URLs retrieved.' % numScraped)
	
	
	print('Scraping articles...')
	scrapedNum = 0 #Articles scraped
	ids = None
	root = None
	for (title, url, date) in articles:
		try:
			source = Source(url, title=title, date = date, scraper=ScraperChuvash, conn=conn)
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
			
		
		
	conn.close()
	
main(numScrape)



