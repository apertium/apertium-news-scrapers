#!/usr/bin/env python3

import requests, lxml, lxml.html

from urllib import request
import urllib.error
import http.client
import sys
import signal

from bs4 import BeautifulSoup
#import unicodedata

from scrapers import ScraperKumukiaAdab
from scraper_classes import Source, Writer


debug = False

domain = "kumukia.ru/adabiat"
domainReal = "kumukia.ru"
siteScraper = ScraperKumukiaAdab
siteLang = "kum"


def getPages():
	#The seed page
	url = "http://kumukia.ru/adabiat/index.php"

	#storing the response received from the GET request
	content = requests.get(url).text

	#extracting the initial list on the navigation bar
	r = content.find("[\n[")

	m = content.find("]\n]")

	first_catch = content[r:m+3]

	first_catch = first_catch.replace("[","").replace("]","").replace('"',"").replace(","," ").replace(":","")

	first_catch = first_catch.replace("p g","p?g")

	first_catch = first_catch.split()

	#forming complete url along with the parameters
	list1=[]
	for i in first_catch:
		list1.append("http://kumukia.ru/adabiat/%s"%(i))

	sys.stdout.write(".")
	sys.stdout.flush()

	#function to make list of parameters from a string (In this case, HTML content of the webpage)
	def make_list(l):
		soup = BeautifulSoup(l)
		m=""
		p=""
		
		for i in soup.find_all("a"):
			m=i.get("onclick" or "onClick")
			if m==None:
				return []
			else:
				p += m

		p = p.replace("doLoads","").replace("(","").replace(")","").replace("amp;","").replace(";"," ").replace("'","").replace("doLoad2","").replace(","," ")

		p = p.split()
		return p

	#To form a list of urls given the list of parameters
	def refiner(p):

		k=[]
	
		for i in range(len(p)):
			if p[i]=="getpage.php" or p[i]== "getmenu.php" or p[i].find("search=worklist")==0 or p[i].find("search=workpage")==0:
				k.append(p[i])
		hp = []

		for i in range(len(k)):
			if i%2!=0:
				hp.append("http://kumukia.ru/adabiat/%s?%s" %  (k[0], k[i]))

		return hp

	newlist = []
	last = []	       
	final = []	       
	h = []
	s=[]
	urls = []

	sys.stdout.write(".")
	sys.stdout.flush()

	#iterating over the initial list to retrieve the child links
	for i in list1:
		p = make_list(requests.get(i).text)
		s+=refiner(p)

	sys.stdout.write(".")
	sys.stdout.flush()
	#iterating over the list of first childs to retrieve their child links
	for i in s:
		p = make_list(requests.get(i).text)
		newlist+=refiner(p)
	
	sys.stdout.write(".")
	sys.stdout.flush()
	#iterating over the links to the work of the authors to retrieve the pages with text.
	for i in newlist:
		p = make_list(requests.get(i).text)
		last+=refiner(p)

	sys.stdout.write(".")
	sys.stdout.flush()
	#eliminating Copies
	for i in last:
		if i not in urls:
			urls.append(i)

	sys.stdout.write(".")
	sys.stdout.flush()

	return urls


if __name__ == "__main__":

	sys.stdout.write("Getting urls.")
	sys.stdout.flush()

	links = getPages()
	# for testing:
	#links=["http://kumukia.ru/adabiat/getpage.php?search=workpage&work=39&page=27", "http://kumukia.ru/adabiat/getpage.php?search=workpage&work=8&page=1"]
	#links=["http://kumukia.ru/adabiat/getpage.php?search=workpage&work=46&page=1", "http://kumukia.ru/adabiat/getpage.php?search=workpage&work=63&page=1"]
	#print("\n".join(links))

	conn = http.client.HTTPConnection(domainReal)
	ids = None
	root = None
	this = 0
	w = Writer()
	
	def term_handler(sigNum, frame):
		print("\nReceived a SIGTERM signal. Closing the program.")
		w.close()
		sys.exit(0)

	signal.signal(signal.SIGTERM, term_handler)
	
	try:
		#for (url, title) in allurls:
		for link in links:
			#sys.stdout.write("\r"+url+" "+title+"\n")
			#sys.stdout.flush()
			this += 1
			try:
				#linkies = link.split('.')
				#url = linkies[0]+"."+urllib.parse.quote(linkies[1], encoding="utf8")
				#print(url)
				url = link
				source = Source(url, scraper=siteScraper, conn=conn)
				source.makeRoot("./", ids=ids, root=root, lang=siteLang)
				msg = "(%s/%s)" % (this, len(links))
				source.add_to_archive(msg=msg)
				if ids is None:   # if not ids:
					ids = source.ids
				if root is None:  # if not root:
					root = source.root
			except Exception as e:
				sys.stdout.write(" — %s \n" % e)
				sys.stdout.flush()
				raise
	except KeyboardInterrupt:
		print("\nReceived a keyboard interrupt. Closing the program.")
	w.close()
	conn.close()

