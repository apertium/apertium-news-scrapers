#!/usr/bin/env python3

from datetime import date, timedelta
from urllib import request
#from lxml import etree
import lxml.html
import lxml.html.clean
from scrapers import ScraperAzattyk
from scraper_classes import Source
import urllib.error
import http.client
import curses
import sys

#urltemplate = "http://www.azattyk.org/archive/%s/%s%02d01/%s/%s.html"
urltemplate = "/archive/%s/%s%02d01/%s/%s.html"

topics = {392: "ky-kyrgyzstan",
	393: "ky-central_asia",
	394: "ky-world",
	395: "ky-politics",
	396: "ky-human_rights",
	397: "ky-economy",
	398: "ky-culture",
	399: "ky-voice_of_people",
	400: "ky-sport"}

startyear = 2009 # 2006
endyear = 2009
minmonth = 1 # 1
maxmonth = 12 # 12

def get_urls(monthurl):  # get the URLS for a given month
	sys.stdout.write("\rGetting %s." % monthurl)
	sys.stdout.flush()

	conn = http.client.HTTPConnection("www.azattyk.org")
	conn.request("GET", monthurl)
	res = conn.getresponse()
	if res.status != 200:
		print(monthurl, res.status, res.reason)
		return
	contents = res.read().decode('utf-8')
	sys.stdout.write(".")
	sys.stdout.flush()

	doc = lxml.html.fromstring(contents)
	mid = doc.find_class("middle_content")[0]

	curdate = ""
	urls = []
	for el in mid.findall(".//li"):
		if "class" in el.attrib:
			if "archive_listrow_date" in el.attrib['class'].split():
				curdate = el.text
		if curdate != "":
			title = None
			url = None
			for a in el.findall(".//a"):
				if "style" not in a.attrib:
					title = a.text
					url = a.attrib["href"]
			if title == None or url == None:
				for a in el.findall(".//a"):
					title = a.text
					url = a.attrib["href"]
				#print(lxml.html.tostring(el)) #lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8'))))
			if title != None and url != None:
				urls.append((url, title))

	sys.stdout.write(".\n")
	sys.stdout.flush()
	conn.close()
	return urls

def get_allurls(startyear, endyear, minmonth, maxmonth):  # get all urls for given date range
	allurls = []

	for year in range(startyear, endyear+1):
		for month in range(minmonth, maxmonth+1):
			for num, topic in topics.items():
				monthurl = urltemplate % (topic, year, month, num, num)
				urls = get_urls(monthurl)

				if urls is not None:
					for url in urls:
						allurls.append(url)
	
	return allurls


def main():
	global startyear, endyear, minmonth, maxmonth

	sys.stdout.write("\rGenerating urls...\n")
	sys.stdout.flush()
	allurls = get_allurls(startyear, endyear, minmonth, maxmonth)

	sys.stdout.write("\r%d articles total\n" % len(allurls))

	conn = http.client.HTTPConnection("www.azattyk.org")

	ids = None
	root = None
	for (url, title) in allurls:
		#sys.stdout.write("\r"+url+" "+title+"\n")
		#sys.stdout.flush()

		try:
			source = Source(url, title=title, scraper=ScraperAzattyk, conn=conn)
			source.makeRoot("./", ids=ids, root=root)
			source.add_to_archive()
			if ids is None:   # if not ids:
				ids = source.ids
			if root is None:  # if not root:
				root = source.root

		except Exception as e:
			sys.stdout.write(str(e))
	
	conn.close()

main()
