import re
import lxml.html
import lxml.html.clean
from urllib import request
from hashlib import sha1
#import time.sleep
from time import sleep

class Scraper(object):
	
	def __init__(self, url, conn=None): #, content):
		self.url = url
		self.conn = conn
		#self.content = content
		self.aid = self.url_to_aid(url)

	def get_content(self):
		if self.conn != None:
			self.conn.request("GET", self.url)
			sleep(0.5)
			res = self.conn.getresponse()
			if res.status != 200:
				#print("\r", self.url, res.status, res.reason)
				#sys.stdout.write("\n\n\r\n", self.url, res.status, res.reason)
				print(res.status, res.reason)
				self.reconnect()
				return False
			self.content = res.read().decode('utf-8')
		else:
			self.content = request.urlopen(self.url).read().decode('utf-8')
		towrite = lxml.html.fromstring(self.content)
		if towrite is not None:
			self.doc = towrite
			return True
		else:
			return False

	def reconnect(self):
		self.conn.close()
		self.conn.connect()


class ScraperKloop(Scraper):
	domain = "kmb3.kloop.kg"
	prefix = "kloop"
	rePagenum = re.compile("p(|age)=([0-9]*)")
	badClasses = ['vk-button', 'mailru-button', 'fb-share-button', 'odkl-button', 'twitter-horizontal', 'live-journal', 'google-buzz', 'mrc__share']


	def scraped(self):
		self.get_content()
		#print(self.doc)
		for el in self.doc.find_class('entrytext'):
			pass
		#return lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8'))).text_content()
		cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
		for className in self.badClasses:
			for el in cleaned.find_class(className):
				el.getparent().remove(el)
		#remove all h3 tags
		for badEl in cleaned.findall(".//h3"):
			badEl.getparent().remove(badEl)

		return cleaned.text_content()

	def url_to_aid(self, url):
		return self.rePagenum.search(url).groups()[1]

class ScraperAzattyk(Scraper):
	domain = "www.azattyk.org"
	prefix = "rferl"
	rePagecode = re.compile("\/([0-9]*)\.html?")

	def scraped(self):
		if self.get_content():
			#print(self.doc)
			el = ""
			for el in self.doc.find_class('zoomMe'):
				pass
			if el == "":
				for ela in self.doc.find_class('boxwidget_part'):
					if "id" in ela.attrib:
						if ela.attrib['id'] == "descText":
							el = ela
			if el != "":
				cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
				#for className in self.badClasses:
				#	for el in cleaned.find_class(className):
				#		el.getparent().remove(el)
				#print(cleaned.text_content())
				return cleaned.text_content()
			else:
				return ""

	def url_to_aid(self, url):
		if self.rePagecode.search(url):
			return self.rePagecode.search(url).groups()[0]
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperAzattyq(Scraper):
	domain = "www.azattyq.org"
	prefix = "rferl"
	rePagecode = re.compile("\/([0-9]*)\.html?")
	rePagecode2 = re.compile("\?id=([0-9]*)")

	def scraped(self):
		if self.get_content():
			#print(self.doc)
			el = ""
			#for el in self.doc.find_class('zoomMe'):
			#print(str(self.doc.find_class('introText')))
			if len(self.doc.find_class('article_txt_intro')) > 0:
				introels = self.doc.find_class('article_txt_intro')
			else:
				introels = None
			if len(self.doc.find_class('articleContent')) > 0:
				for el in self.doc.find_class('articleContent'):
					pass
				#print(str(el))
				if lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')) != "":
				#if el. is None:
					#if self.doc.get_element_by_id('introText'):
					try:
						el = self.doc.get_element_by_id('introText')
					except KeyError:
						pass
					#print("INTROTEXT")
			else:
				el = self.doc.get_element_by_id('introText')
				#print("INTROTEXT")
			#elif len(self.doc.find_class('introText')) > 0:
			#	for el in self.doc.find_class('introText'):
			#		pass
			#if el == "":
			#	for ela in self.doc.find_class('boxwidget_part'):
			#		if "id" in ela.attrib:
			#			if ela.attrib['id'] == "descText":
			#				el = ela
			if el != "" and el != None:
				#to_return = ""
				cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
				for style in cleaned.findall(".//style"):
					style.drop_tree()
				#for p in el.iter("p"):
					#cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el, pretty_print=True).decode('utf-8')))
					##print(cleaned.text_content)
					##cleaned = cleaned.
				#for br in cleaned.xpath('//br'):
				for br in cleaned.findall(".//br"):
					if br.tail:
						br.tail="\n"+br.tail
					else:
						br.tail="\n"
					#print(br.tail)
				#for p in cleaned.xpath('//p'):
				for p in cleaned.findall('.//p'):
					if p.tail:
						p.tail="\n"+p.tail
					else:
						p.tail="\n"
					#print(p)
				##to_return += cleaned.text_content()+"\n"
				to_return = cleaned.text_content()+"\n"
				toadd = ""
				if introels is not None:
					for introel in introels:
						toadd += introel.text_content()+"\n"
				to_return = toadd + to_return
				#print(to_return)
				##for className in self.badClasses:
				##	for el in cleaned.find_class(className):
				##		el.getparent().remove(el)
				##print(cleaned.text_content())
				#return cleaned.text_content()
				to_return = re.sub('\n\n\n*', '\n', to_return)
				to_return = to_return.strip('\n')
				return to_return
			else:
				return ""

	def url_to_aid(self, url):
		if self.rePagecode.search(url):
			idsofar = self.rePagecode.search(url).groups()[0]
			if idsofar!="330":
				return idsofar
			else:
				if self.rePagecode2.search(url):
					idsofar = self.rePagecode2.search(url).groups()[0]
					return idsofar
				else:
					return sha1(url.encode('utf-8')).hexdigest()
		else:
			return sha1(url.encode('utf-8')).hexdigest()



class ScraperTRT(Scraper):
	domain = "www.trtkyrgyz.com"
	prefix = "trt"
	rePagecode = re.compile("haberkodu=([0-9a-f\-]*)(.html)?")

	def scraped(self):
		self.get_content()
		cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(self.content))
		output = ""
		for el in cleaned.findall(".//p"):
			#for subel in el.getiterator():
			#	output += subel.text
			output += el.text_content()
			#print(el.text)
		return output

		#print(self.url)
	
	def url_to_aid(self, url):
		return self.rePagecode.search(url).groups()[0]

class ScraperBBC(Scraper):
	domain = "www.bbc.co.uk"
	prefix = "bbc"
	
	def scraped(self):
		self.get_content()
		el = None
		for el in self.doc.find_class('bodytext'):
			pass
		if el != None:
			cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
			return cleaned.text_content()
		else:
			return False

	def url_to_aid(self, url):
		return sha1(url.encode('utf-8')).hexdigest()

class ScraperAlaman(Scraper):
	domain = "alamankg.org"
	prefix = "alaman"
	reArticleNum = re.compile("\/([0-9]*?)\/?$")
	reBadDomain = re.compile("^http://alaman\\.kg/(.*)")

	def __init__(self, url):
		# Alaman's rss feed points urls in a domain that forwards to the correct domain but without the content; this logic corrects the domain
		if self.reBadDomain.match(url):
			self.url = self.reBadDomain.sub('http://alamankg.org/\g<1>', url)
			print(">> "+self.url)
		else:
			self.url = url

		self.aid = self.url_to_aid(url)

	def scraped(self):
		self.get_content()
		el = None
		for el in self.doc.find_class('viewnew'):
			pass
		if el != None:
			cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
			return cleaned.text_content()
		else:
			return False

	def url_to_aid(self, url):
		return self.reArticleNum.search(url).groups()[0]
