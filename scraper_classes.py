#!/usr/bin/env python3

import re, urllib, os #feedparser, 
from bottle import template
from hashlib import sha1
#from html_parser import MyHTMLParser
#from scraper_parsers import *
from scrapers import *
import rssfucker
from lxml import etree
from datetime import datetime
import sys


class Feed(object):

	domain_name = re.compile('^http[s]{0,1}://(.*?)/.*')

	feed_sites = {
		"www.trtkyrgyz.com": ScraperTRT,
		"www.azattyk.org": ScraperAzattyk,
		"kmb3.kloop.kg": ScraperKloop,
		"www.bbc.co.uk": ScraperBBC,
		"alamankg.org": ScraperAlaman
	}

	which_scraper = None;
	feed = None;

	def __init__(self, url):
		self.which_scraper = self.get_scraper(url)
		#self.feed = feedparser.parse(url)
		self.feed = rssfucker.parse_rss(url)
		#print(self.feed)
		
	def get_sources(self):
		#for item in self.feed["entries"]:
		for title, link in self.feed.items():
			#for link in item["links"]:
			#	title = item["title"]
			#	print('++' , title);
			#	print('++' , item["link"]);
			#	thisScraper = self.which_scraper
			#	yield Source(item["link"], scraper=thisScraper, title=title)
			print('++' , title);
			print('++' , link);
			thisScraper = self.which_scraper
			yield Source(link, scraper=thisScraper, title=title)

	
	def get_scraper(self, url):
		domain = self.domain_name.match(url).group(1)
		which_scraper = self.feed_sites.get(domain)
		if which_scraper == None:
			raise Exception("Can't get scraper!")
		else:
			return which_scraper
		#else: Feed(url, which_scraper)


class Source(object):
	aid = None
	scraper = None
	parser = None
	filename = None
	page_contents = None
	out_content = None

	def __init__(self, url, scraper=None, title=None, conn=None):
		self.url = url
		self.title = title
		self.conn = conn
		if not scraper:
			self.scraper = self.get_scraper(url)
		else: self.scraper = scraper
		if not self.scraper:
			raise Exception("No scraper set!")	

		#self.makeRoot()

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
			#self.page_contents = self.get_page(self.url)
			#self.out_content = self.get_content()
			#parser = self.parser
			#print(self.page_contents.split('\n')[914])
			#try:
			#	parser.feed(self.page_contents)
			#except Exception:
			#	pass
			#self.out_content = parser.get_content()
			print("Adding...", end=" ")
			self.out_content = scraper.scraped()

			#print(outdir, self.filename, self)
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
		#print(self.ids)

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
		else:
			self.root = root
		if not ids:
			self.populateIds()
		else:
			self.ids = ids
		sys.stdout.write(".")
		sys.stdout.flush()

	

	def add_to_archive(self, msg=None):
		scraper = self.scraper(self.url, conn=self.conn)
		self.aid = scraper.aid
		self.entry_id = self.scraper.prefix +"."+ self.aid
		if self.entry_id not in self.ids:
			#print("Adding...", end=" ")
			sys.stdout.write("\r")
			if msg is not None:
				sys.stdout.write(msg+" ")
			#else:
			#	sys.stdout.write("\r")
			sys.stdout.write("Adding %s ." % self.url)
			sys.stdout.flush()
			self.out_content = scraper.scraped()
			sys.stdout.write(".")
			if self.out_content:
				outTime = datetime.now().isoformat()
				#print(self.root, self.url, self.entry_id, self.title, outTime, self.out_content)
				etree.SubElement(self.root, "entry", source=self.url, id=self.entry_id, title=self.title, timestamp=outTime).text = self.out_content
				#print(outdir, self.filename, self)
				etree.ElementTree(self.root).write(self.path, pretty_print=True, encoding='UTF-8', xml_declaration=False)
				#print("added.")
				sys.stdout.write(". added!\n")
				sys.stdout.flush()
				self.ids += [self.aid]
			else:
				#print("empty content, not added.")
				sys.stdout.write("empty content, not added.\n")
				sys.stdout.flush()

		else:
			#print(self.entry_id, " exists!  Skipping. :(")
			sys.stdout.write("\r"+self.entry_id+" exists!  Skipping.\n")
			sys.stdout.flush()



class SimpleHtmlScraper(object):
	def url_to_aid(self, url):
		return sha1(url.encode('utf-8')).hexdigest()

	def __init__(self, prefix, url, outdir):
		self.url = url
		self.prefix = prefix
		self.outdir = outdir
		self.aid = self.url_to_aid(url)
		#self.filename = self.prefix+".%s.html" % self.aid
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
