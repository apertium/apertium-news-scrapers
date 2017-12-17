## This program scrapes news articles from the website http://altaicholmon.ru/.

from lxml import html
from datetime import date, timedelta
from scrapers import ScraperAltaicholmon
from scraper_classes import Source, Writer
import http.client
import string
import requests
import time
import sys

homepage = "http://altaicholmon.ru/news/allnews/"

translator = str.maketrans(dict.fromkeys("\n\t"))

articles = []

def populateArticleList(pageNum): #adds article information to the article list
	page = requests.get(homepage + "page/" + str(pageNum))
	tree = html.fromstring(page.content)
	hrefs = tree.xpath('//div[@class="col-md-8 border_right_main_news"]/a[@class="link link-news"]/@href')
	titles = tree.xpath('//h3[@class="h3-theme-cholmon"]/text()')
	dates = tree.xpath('//p[@class="news_avtor_date"]/text()')
	
	for i in range(0, len(hrefs)):
		titles[i] = str(titles[i]).translate(translator).strip()
		dates[i] = str(dates[i]).translate(translator).strip()
		articles.append((hrefs[i], titles[i], dates[i]))		
		
def getLastPage(): #calculates the number of pages on the news website
		tree = html.fromstring(requests.get(homepage).content)
		lastPage = str(tree.xpath('//div[@class="wp-pagenavi"]/a[@class="last"]/@href')[0])
		lastPageNum = ""

		for i in range(0, len(lastPage)):
			if lastPage[i].isdigit():
				lastPageNum = lastPageNum + lastPage[i]
		
		return int(lastPageNum)
	
def term_handler(sigNum, frame):
	print("\nReceived a SIGTERM signal. Closing the program.")
	w.close()
	sys.exit(0)	
	
def main():
	conn = http.client.HTTPConnection("altaicholmon.ru")
	ids = None
	root = None
	w = Writer()

	for i in range(0, getLastPage() + 2): populateArticleList(i + 1)
	try:
		for (url, title, date) in articles:
			try:
				source = Source(url, title=title, date=date, scraper=ScraperAltaicholmon, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang="alt")
				source.add_to_archive()
				if ids is None:
					ids = source.ids
				if root is None:
					root = source.root
			except Exception as e:
				print(url + " " + str(e))
	except KeyboardInterrupt:
		print("\nReceived a keyboard interrupt. Closing the program.")
	w.close()
	conn.close()			  

main()
