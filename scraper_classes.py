#!/usr/bin/env python3

import re, urllib, os
from bottle import template
from hashlib import sha1
from scrapers import *
import rssfucker
from lxml import etree
import lxml.html
from lxml.html import clean
from datetime import datetime
from threading import Thread
import sys

urlMatcher = re.compile('^(http(s?)\:\/\/|~/|/)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?/?(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?')

treeToWrite = None	# etree for Writer's writeToDisk()
pathToWrite = None	# path for Writer's writeToDisk()

class Feed(object):

	domain_name = re.compile('^http[s]{0,1}://(.*?)/.*')

	feed_sites = {
		"www.trtkyrgyz.com": ScraperTRT,
		"www.azattyk.org": ScraperAzattyk,
		"www.azattyq.org": ScraperAzattyq,
		"www.azathabar.com": ScraperAzathabar,
		"kmb3.kloop.kg": ScraperKloop,
		"www.bbc.co.uk": ScraperBBC,
		"alamankg.org": ScraperAlaman,
		"www.news.mn": ScraperNewsmn,
		"www.azatutyun.am": ScraperAzatutyun,
		"www.chuvash.org": ScraperChuvash,
		"www.azadliq.org": ScraperAzadliq,
		"kumukia.ru": ScraperAKumukia,
		"kumukia.ru/adabiat": ScraperKumukiaAdab,
		"www.radioerkinli.com": ScraperErkinli
	}		

	which_scraper = None;
	feed = None;

	def __init__(self, url):
		self.which_scraper = self.get_scraper(url)
		self.feed = rssfucker.parse_rss(url)
		
	def get_sources(self):
		for title, link in self.feed.items():
			print('++' , title);
			print('++' , link);
			thisScraper = self.which_scraper
			yield Source(link, scraper=thisScraper, title=title)

	
	def get_scraper(self, url):
		domain = self.domain_name.match(url).group(1)
		which_scraper = self.feed_sites.get(domain)
		if not which_scraper:
			raise Exception("Can't get scraper!")
		else:
			return which_scraper

class Source(object):

	aid = None
	scraper = None
	parser = None
	filename = None
	page_contents = None
	out_content = None

	def __init__(self, url, date = None, scraper=None, title=None, conn=None):
		self.url = url
		self.title = title
		self.conn = conn
		self.date = date

		if not scraper:
			self.scraper = self.get_scraper(url)
		else: 
			self.scraper = scraper
		self.domain = self.scraper.domain
		if not self.scraper:
			raise Exception("No scraper set!")
		
	def get_scraper(self, url):
		return
		
	def get_page(self, link):
		print("DEBUG: "+str(self.conn))
		if self.conn != None:
			self.conn.request("GET", link)
			res = self.conn.getresponse()
			if res.status != 200:
				print(link, res.status, res.reason)
				return
			return res.read().decode('utf-8')

		else:
			f = urllib.request.urlopen(link)
			return f.read().decode('utf-8')

	def filename_exists(self):
		return os.path.isfile(self.path)
	
	def add_to_archive_old(self, outdir):
		scraper = self.scraper(self.url) #, self.page_contents)
		self.aid = scraper.aid
		self.filename = self.scraper.prefix+".%s.html" % self.aid

		self.outdir = outdir
		self.path = os.path.join(self.outdir, self.filename)

		if not self.filename_exists():
			print("Adding...", end=" ")
			self.out_content = scraper.scraped()

			with open(os.path.join(self.path), 'w+') as f:
				f.write(template('source', title=self.title, content=self.out_content, url = self.url))
			print("added.")

		print(self.filename, " exists!  Skipping.")

	def populateIds(self):
		self.ids = []
		sys.stdout.write("\rPopulating ids.")
		sys.stdout.flush()
		for item in self.root.getiterator("{http://apertium.org/xml/corpus/0.9}entry"):
			self.ids += [item.attrib['id']]
		sys.stdout.write(".\n")
		sys.stdout.flush()

	def makeRoot(self, outdir, ids=None, root=None, lang="ky"):
		sys.stdout.write("\r.")
		sys.stdout.flush()
		self.outdir = outdir
		self.filename = self.scraper.prefix+".xml"
		self.path = os.path.join(self.outdir, self.filename)

		sys.stdout.write(".")
		sys.stdout.flush()
		if root is None:
			if os.path.isfile(self.path):
				self.root = etree.parse(self.path).getroot()
			else:
				self.root = etree.Element("corpus", xmlns="http://apertium.org/xml/corpus/0.9", language=lang, name=self.scraper.prefix)
				treeToWrite = self.root
		else:
			self.root = root
		if not ids:
			self.populateIds()
		else:
			self.ids = ids
		sys.stdout.write(".")
		sys.stdout.flush()

	def add_to_archive(self, msg=None):
		scraper = self.scraper(self.url, self.date, conn=self.conn, source=self)
		self.aid = scraper.aid
		self.entry_id = self.scraper.prefix +"."+ self.aid
		if self.entry_id not in self.ids:

			sys.stdout.write("\r")
			if msg is not None:
				sys.stdout.write(msg+" ")

			sys.stdout.write("Adding %s ." % self.url)
			sys.stdout.flush()
			self.out_content = scraper.scraped()
			self.date = scraper.date
			sys.stdout.write(".")
			if urlMatcher.match(self.url):
				self.fullurl = self.url
			else:
				self.fullurl = "http://%s%s" % (self.domain, self.url)

			if self.out_content:
				outTime = datetime.now().isoformat()

				etree.SubElement(self.root, "entry", source=self.fullurl, id=self.entry_id, title=self.title, timestamp=outTime, date = "" if self.date is None else str(self.date)).text = self.out_content
				
				global treeToWrite, pathToWrite
				treeToWrite = etree.ElementTree(self.root)
				pathToWrite = self.path

				sys.stdout.write(". added!\n")
				sys.stdout.flush()
				self.ids += [self.aid]
			else:
				sys.stdout.write("empty content, not added.\n")
				sys.stdout.flush()

		else:
			sys.stdout.write("\r"+self.entry_id+" exists!  Skipping.\n")
			sys.stdout.flush()

class Writer(Thread):
	def __init__(self, writingInterval=60):
		if writingInterval < 1:
			print("The given writing interval is not possible. Defaulting to 60 seconds.")
			self.writingInterval = 60
		print("Writer started")
		self.writingInterval = writingInterval
		self.writing = True
		self.closingThread = False
		thread = Thread(target=self.run, args=())
		thread.daemon = True
		thread.start()

	def run(self):
		while self.closingThread == False:
			for i in range(self.writingInterval):
				if self.closingThread:
					break
				else:
					time.sleep(1)
			if self.closingThread == True:
				break
			else:
				self.writeToDisk()
		self.writing = False

	def close(self):
		self.closingThread = True
		while self.writing: # waiting until writing has ended
			time.sleep(1)
		self.writeToDisk()
		print("Writer closed")

	def writeToDisk(self):
		if pathToWrite is not None and treeToWrite is not None:
			treeToWrite.write(pathToWrite, pretty_print=True, encoding='UTF-8', xml_declaration=False)

class SimpleHtmlScraper(object):
	def url_to_aid(self, url):
		return sha1(url.encode('utf-8')).hexdigest()

	def __init__(self, prefix, url, outdir):
		self.url = url
		self.prefix = prefix
		self.outdir = outdir
		self.aid = self.url_to_aid(url)
		self.filename = "%s.%s.html" % (self.prefix, self.aid)
		self.title = ""
		self.content = ""
		self.path = os.path.join(self.outdir, self.filename)
	
	def write(self):
		if self.url_not_in_path():
			with open(self.path, 'w+') as f:
				f.write(template('source', title=self.title, content=self.content, url = self.url))
	
	def parse(self):
		if self.url_not_in_path():
			content = urllib.request.urlopen(self.url)
			page = content.read().decode('utf-8')
			myparser = HTMLParserSimple()
			myparser.feed(page)
			(self.title, self.content) = myparser.get_pages()

	def url_not_in_path(self):
		return not os.access(self.path, os.F_OK)