#!/usr/bin/env python3

from datetime import date
import lxml.html
import http.client
from scraper_classes import Source
from scrapers import ScraperNewsmn

startDate = date(2011, 12, 1)
endDate = date(2011, 12, 2)

urlTemplate = "/archive.shtml?q=&from=%s&to=%s&sortBy=NEWEST&page=%s"

articles = []

def getPage(conn, url):
	conn.request("GET", url)
	res = conn.getresponse()
	if res.status != 200:
		print(url, res.status, res.reason)
		return
	contents = res.read().decode('utf-8')
	doc = lxml.html.fromstring(contents)
	return doc

def printArticles(articlesData, fileName, display=False):
	if display:
		for (title, url) in articlesData:
			print(title, url)
	else:
		with open(fileName, 'a', encoding='utf-8') as file:
			for (title, url) in articlesData:
				file.write("%s, %s\n" % (title, url))

def populateArticlesList(conn):
	url = urlTemplate % (startDate.isoformat(), endDate.isoformat(),1)
	doc = getPage(conn, url)
	numTag = str(lxml.html.tostring(doc.find_class("search-result")[0]))
	numArticles = int(numTag[numTag.find('/')+2 : numTag.find("</")])
    
	for i in range(1,int(numArticles/20)+2):
		url = urlTemplate % (startDate.isoformat(), endDate.isoformat(),i)
		doc = getPage(conn, url)
		titleTags = doc.find_class("bd-list-title")
		if len(titleTags) is 0:
			break
		for titleTag in titleTags:
			for article in titleTag:
				title = (article.text).strip()
				url = article.attrib["href"]
				articles.append((title, url))
	print("%s Articles scraped from %s to %s" % (str(len(articles)), startDate, endDate))
	
def main(startDate, endDate):
	conn = http.client.HTTPConnection("archive.news.mn")
	populateArticlesList(conn)
	ids = None
	root = None
	for (title, url) in articles:
		if url.find("video.news") + url.find("id.news") + url.find("english.news") + url.find("photoalbum") is -4:
			try:
				source = Source(url, title=title, scraper=ScraperNewsmn, conn=conn)
				source.makeRoot("./", ids=ids, root=root)
				source.add_to_archive()
				if ids is None:
					ids = source.ids
				if root is None:
					root = source.root
					
				# doc = getPage(conn, url)
				# content = None
				
				# if len(doc.xpath("//div[@style='text-align: justify;']")) is not 0:
					# content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(doc.xpath("//div[@style='text-align: justify;']")[0]).decode('utf-8'))).text_content().strip()
				# elif len(doc.xpath("//p[@style='text-align: justify;']")) is not 0:
					# content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(doc.xpath("//p[@style='text-align: justify;']")[0]).decode('utf-8'))).text_content().strip()
				# elif len(doc.find_class("text")) is not 0:
					# content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(doc.find_class("text")[0]).decode('utf-8'))).text_content().strip()
				# elif len(doc.find_class("read-bd-body")) is not 0:
					# content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(doc.find_class("read-bd-body")[0]).decode('utf-8'))).text_content().strip()
				
				# with open(fileName, 'a', encoding='utf-8') as file:
					# content = ''.join(content.splitlines())
					# file.write(url + " " + content + '\n')
			except Exception as e:
				print(url + " " + str(e))

fileName = 'test.txt'
with open(fileName, 'w'):
    pass
main(startDate, endDate)
printArticles(articles, fileName) #, display=True)
