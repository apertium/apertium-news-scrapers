#!/usr/bin/env python3

from lxml import html
from scrapers import ScraperKhakaschiry
from scraper_classes import Source, Writer
import http.client
import string
import requests
import time
import sys

homepage = "http://khakaschiry.ru/news/"

translator = str.maketrans(dict.fromkeys("\n\t"))

articles = []

def populateArticleList(pageNum): #adds article information to the article list
    page = requests.get(homepage + "?PAGEN_1=" + str(pageNum))
    tree = html.fromstring(page.content)
    hrefs = tree.xpath('//div[@class="category-news-item"]/a[@class="green"]/@href')
    titles = tree.xpath('//div[@class="category-news-item"]/a[@class="green"]/text()')
    dates = tree.xpath('//div/span[@class="news-date-time"]/text()')
    
    for i in range(0, len(hrefs)):
        hrefs[i] = "http://khakaschiry.ru" + hrefs[i]
        titles[i] = str(titles[i]).translate(translator).strip()
        dates[i] = str(dates[i]).translate(translator).strip()
        articles.append((hrefs[i], titles[i], dates[i]))    
		
def getLastPage(): #calculates the number of pages on the news website
        tree = html.fromstring(requests.get(homepage).content)
        lastPage = str(tree.xpath('//font[@class="text"]/a[contains(text(), "Конец")]/@href')[0])
        
        index = lastPage.index("PAGEN_1=")
        lastPageNum = lastPage[index + 8:]
		
        return int(lastPageNum)
	
def term_handler(sigNum, frame):
	print("\nReceived a SIGTERM signal. Closing the program.")
	w.close()
	sys.exit(0)	
	
def main():
    conn = http.client.HTTPConnection("khakaschiry.ru")
    ids = None
    root = None
    w = Writer()
    
    for i in range(0, getLastPage()): populateArticleList(i + 1)
    
    try:
        for (url, title, date) in articles:
            try:
                source = Source(url, title = title, date = date, scraper = ScraperKhakaschiry, conn = conn)
                source.makeRoot("./", ids = ids, root = root, lang = "kjh")
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
