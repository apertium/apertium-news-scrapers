import re
import lxml.html
#from lxml import etree
from lxml.html import builder as E
import lxml.html.clean
from urllib import request
import urllib.parse
from hashlib import sha1
#import time.sleep
from time import sleep
import time
import html.parser

h = html.parser.HTMLParser()

class Scraper(object):
	
	def __init__(self, url, date="", conn=None, source = None): #, content):
		self.url = url
		self.conn = conn
		#self.content = content
		self.aid = self.url_to_aid(url)
		self.date = date
		self.source = source

	def get_content(self, encoding='utf-8'):
		self.reconnect()
		if self.conn != None:
			self.conn.request("GET", self.url)
			sleep(0.5)
			res = self.conn.getresponse()
			if res.status != 200:
				#print("\r", self.url, res.status, res.reason)
				#sys.stdout.write("\n\n\r\n", self.url, res.status, res.reason)
				print(res.status, res.reason)
				print(self.url)
				self.reconnect()
				return False
			
			self.content = res.read().decode(encoding).encode('utf-8').decode('utf-8').replace('\r', ' ') #replace clears residual \r from '\r\n' in html
		else:
			self.content = request.urlopen(self.url).read().decode(encoding).replace('\r', ' ')
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
				for el in cleaned.find_class("embedded_content_object"):
					el.getparent().remove("embedded_content_object")
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

class ScraperAzathabar(Scraper):
	domain = "www.azathabar.com"
	prefix = "rferl"
	rePagecode = re.compile("\/([0-9]*)\.html?")
	rePagecode2 = re.compile("\?id=([0-9]*)")

	def scraped(self):
		#FIXME: check
		if self.get_content():
			#print(self.doc)
			el = ""

			dateEl = self.doc.find_class('article_date')
			if len(dateEl)==0:
				dateEl = self.doc.find_class('date')
			dateBlah = dateEl[0].text_content().strip('\r\n	 ')
			if re.match("[0-9]{2}\.[0-9]{2}\.[0-9]{4}", dateBlah):
				self.date = time.strftime('%Y-%m-%d', time.strptime(dateBlah, "%d.%m.%Y"))
			else:
				dateBlah = re.sub('.*([0-9]{2}\.[0-9]{2}\.[0-9]{4} [0-9]{2}:[0-9]{2}).*', '\\1', dateBlah)
				self.date = time.strftime('%Y-%m-%dT%H:%M', time.strptime(dateBlah, "%d.%m.%Y %H:%M"))

			if len(self.doc.find_class('article_txt_intro')) > 0:
				introels = self.doc.find_class('article_txt_intro')
			else:
				introels = None
			if len(self.doc.find_class('articleContent')) > 0:
				for el in self.doc.find_class('articleContent'):
					pass
				#print(str(el))
				if len(el.find_class('zoomMe')) > 0:
					el = el.find_class('zoomMe')[0]
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

			#for el in self.doc.find_class('zoomMe'):
			#	pass
			#if el == "":
			#	for ela in self.doc.find_class('boxwidget_part'):
			#		if "id" in ela.attrib:
			#			if ela.attrib['id'] == "descText":
			#				el = ela
			if el != "":
				cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
				#for className in self.badClasses:
				#	for el in cleaned.find_class(className):
				#		el.getparent().remove(el)
				#print(cleaned.text_content())
				#return cleaned.text_content()
				for style in cleaned.findall(".//style"):
					style.drop_tree()
				for br in cleaned.findall(".//br"):
					if br.tail:
						br.tail="\n"+br.tail
					else:
						br.tail="\n"
				for p in cleaned.findall('.//p'):
					if p.tail:
						p.tail="\n"+p.tail
					else:
						p.tail="\n"
				to_return = cleaned.text_content()+"\n"
				toadd = ""
				if introels is not None:
					for introel in introels:
						toadd += introel.text_content()+"\n"
				to_return = toadd + to_return

				to_return = re.sub('\r\n*', '\n', to_return)
				to_return = re.sub('\n\n\n*', '\n', to_return)
				#print(to_return)
				to_return = to_return.strip('\n \t')
				return to_return

			else:
				return ""

	def url_to_aid(self, url):
		if self.rePagecode.search(url):
			idsofar = self.rePagecode.search(url).groups()[0]
			if len(idsofar) > 4:
				return idsofar
			else:
				idsofar = self.rePagecode2.search(url).groups()[0]
				return idsofar
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperOlloo(Scraper):
	domain = "www.olloo.mn"
	prefix = "olloo"

	def scraped(self):
		self.get_content('cp1251')
		cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class('content')[1]).decode('utf-8')))
		cleaned = cleaned.text_content()
		cleaned = h.unescape(cleaned)
		cleaned = h.unescape(cleaned).replace("\r", "") #remove extra carriage returns
		cleaned = cleaned.replace('V', 'Ү')
		cleaned = cleaned.replace('v', 'ү')
		cleaned = cleaned.replace('Є', 'Ө')
		cleaned = cleaned.replace('є', 'ө')
		return cleaned

	def url_to_aid(self, url):
		uid = url.split("&sid=")[1]
		if uid is not None:
			return uid
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperBolod(Scraper):
	domain = "www.bolod.mn"
	prefix = "bolod"

	def scraped(self):
		self.get_content()
		cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.xpath("//div[@align='justify']")[0]).decode('utf-8')))
		cleaned = cleaned.text_content()
		cleaned = h.unescape(cleaned).replace("\r", "") #remove extra carriage returns
		return cleaned.strip()

	def url_to_aid(self, url):
		uid = url.split("&nID=")[1]
		if uid is not None:
			return uid
		else:
			return sha1(url.encode('utf-8')).hexdigest()
	
class ScraperNewsmn(Scraper):
	domain = "www.news.mn"
	prefix = "newsmn"
	
	def scraped(self):
		self.get_content()
		if len(self.doc.xpath("//div[@style='text-align: justify;']")) is not 0:
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.xpath("//div[@style='text-align: justify;']")[0]).decode('utf-8'))).text_content().strip()
		elif len(self.doc.xpath("//p[@style='text-align: justify;']")) is not 0:
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.xpath("//p[@style='text-align: justify;']")[0]).decode('utf-8'))).text_content().strip()
		elif len(self.doc.find_class("text")) is not 0:
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class("text")[0]).decode('utf-8'))).text_content().strip()
		elif len(self.doc.find_class("read-bd-body")) is not 0:
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class("read-bd-body")[0]).decode('utf-8'))).text_content().strip()
		return content

	def url_to_aid(self, url):
		endUrl = url.split('content/')[1]
		aid = endUrl[:endUrl.find('.shtml')]
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()
			
class ScraperAzatutyun(Scraper):
	domain = "www.azatutyun.am"
	prefix = "azatutyun"
	badClasses = ['mediaplayer audioplayer','cannot-play j_errorContainer', 'downloadlinkstatic', 'playlistlink', 'expandMediaClose']
	
	def scraped(self):
		self.get_content()
		contentFinal = ""
		for zoomMeTag in self.doc.find_class("zoomMe"):
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(zoomMeTag).decode('utf-8')))
			if len(content.text_content()) > len(contentFinal.text_content() if contentFinal != "" else contentFinal):
				contentFinal = content
		for className in self.badClasses:
			for el in contentFinal.find_class(className):
				el.getparent().remove(el)
		return contentFinal.text_content().strip()

	def url_to_aid(self, url):
		endUrl = url.split('article/')[1]
		aid = endUrl[:endUrl.find('.html')]
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperChuvash(Scraper):
	domain = "www.chuvash.org"
	prefix = "chuvash"
	
	def scraped(self):
		self.get_content()
		for el in self.doc.xpath("//span[@style='font-family:Verdana;font-size:10px;']"):
			el.getparent().remove(el)
		content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class("hipar_text")[0]).decode('utf-8'))).text_content().strip()
		if self.source is not None:
			self.source.title = self.doc.xpath("//span[@style='color:#af2900;']")[0].text_content()
		try:
			date = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class("tags")[0]).decode('utf-8'))).text_content().strip()
			date = re.findall('[0-9]{2}\.[0-9]{2}\.[0-9]{4}', date)[0]
			self.date = time.strftime('%Y-%m-%d', time.strptime(date, "%d.%m.%Y"))
		except:
			self.date = None
		return content
		
	def url_to_aid(self, url):
		aid = url.split('news/')[1].replace('.html','')
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()
			
class ScraperAzadliq(Scraper):
	domain = "www.azadliq.org"
	prefix = "azadliq"
	badClasses = ['mediaplayer audioplayer','cannot-play j_errorContainer', 'downloadlinkstatic', 'playlistlink', 'expandMediaClose']
	
	def scraped(self):
		self.get_content()
		contentFinal = ""
		for zoomMeTag in self.doc.find_class("zoomMe"):
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(zoomMeTag).decode('utf-8')))
			if len(content.text_content()) > len(contentFinal.text_content() if contentFinal != "" else contentFinal):
				contentFinal = content
		for className in self.badClasses:
			for el in contentFinal.find_class(className):
				el.getparent().remove(el)
		return contentFinal.text_content().strip()

	def url_to_aid(self, url):
		if 'archive/news' in url:
			aid = url.split('?id=')[1]
		else:
			urlSplit = re.findall('[0-9]{6,8}\.html$', url)
			if len(urlSplit):
				aid = urlSplit[0].replace('.html','')
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()
			
class ScraperHypar(Scraper):
	domain = "www.hypar.ru"
	prefix = "hypar"
	
	def scraped(self):
		self.get_content(encoding = 'cp1251')
		content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(self.doc.find_class("txt_p")[0]).decode('utf-8'))).text_content().strip()
		return content
	
	def url_to_aid(self, url):
		aid = url.split('32/')[1].replace(r'/index.php','')
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperOzodlik(Scraper):
	domain = "www.ozodlik.org"
	prefix = "uzb.rferl"
	rePagecode = re.compile("\/([0-9]*)\.html?")
	rePagecode2 = re.compile("\?id=([0-9]*)")

	def scraped(self):
		#FIXME: check
		if self.get_content():
			#print(self.doc)
			el = ""

			self.get_date()

			if len(self.doc.find_class('article_txt_intro')) > 0:
				introels = self.doc.find_class('article_txt_intro')
			else:
				introels = None
			if len(self.doc.find_class('articleContent')) > 0:
				for el in self.doc.find_class('articleContent'):
					pass
				#print(str(el))
				if len(el.find_class('zoomMe')) > 0:
					el = el.find_class('zoomMe')[0]
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

			#for el in self.doc.find_class('zoomMe'):
			#	pass
			#if el == "":
			#	for ela in self.doc.find_class('boxwidget_part'):
			#		if "id" in ela.attrib:
			#			if ela.attrib['id'] == "descText":
			#				el = ela
			if el != "":
				cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
				#for className in self.badClasses:
				#	for el in cleaned.find_class(className):
				#		el.getparent().remove(el)
				#print(cleaned.text_content())
				#return cleaned.text_content()
				for videodownload in cleaned.find_class("downloadvideoico"):
					videodownload.drop_tree()
				for style in cleaned.findall(".//style"):
					style.drop_tree()
				for br in cleaned.findall(".//br"):
					if br.tail:
						br.tail="\n"+br.tail
					else:
						br.tail="\n"
				for p in cleaned.findall('.//p'):
					if p.tail:
						p.tail="\n"+p.tail
					else:
						p.tail="\n"
				to_return = cleaned.text_content()+"\n"
				toadd = ""
				if introels is not None:
					for introel in introels:
						toadd += introel.text_content()+"\n"
				to_return = toadd + to_return

				to_return = re.sub('\r\n*', '\n', to_return)
				to_return = re.sub('\n\n\n*', '\n', to_return)
				#print(to_return)
				to_return = to_return.strip('\n \t')
				return to_return

			else:
				return ""

	def get_date(self):
		dateEl = self.doc.find_class('article_date')
		if len(dateEl)==0:
			dateEl = self.doc.find_class('date')
		dateBlah = dateEl[0].text_content().strip('\r\n	 ')
		if re.match("^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$", dateBlah):
			self.date = time.strftime('%Y-%m-%d', time.strptime(dateBlah, "%d.%m.%Y"))
		else:
			dateBlah = re.sub('.*([0-9]{2}\.[0-9]{2}\.[0-9]{4} [0-9]{2}:[0-9]{2}).*', '\\1', dateBlah)
			self.date = time.strftime('%Y-%m-%dT%H:%M', time.strptime(dateBlah, "%d.%m.%Y %H:%M"))

	def url_to_aid(self, url):
		if self.rePagecode.search(url):
			idsofar = self.rePagecode.search(url).groups()[0]
			if len(idsofar) > 4:
				return idsofar
			else:
				idsofar = self.rePagecode2.search(url).groups()[0]
				return idsofar
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperSvoboda(Scraper):
	domain = "www.radiosvoboda.org"
	prefix = "ukr.rferl"
	rePagecode = re.compile("\/([0-9]*)\.html?")
	rePagecode2 = re.compile("\?id=([0-9]*)")

	def scraped(self):
		#FIXME: check
		if self.get_content():
			#print(self.doc)
			el = ""

			self.get_date()

			if len(self.doc.find_class('article_txt_intro')) > 0:
				introels = self.doc.find_class('article_txt_intro')
			else:
				introels = None
			if len(self.doc.find_class('articleContent')) > 0:
				for el in self.doc.find_class('articleContent'):
					pass
				#print(str(el))
				if len(el.find_class('zoomMe')) > 0:
					el = el.find_class('zoomMe')[0]
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

			#for el in self.doc.find_class('zoomMe'):
			#	pass
			#if el == "":
			#	for ela in self.doc.find_class('boxwidget_part'):
			#		if "id" in ela.attrib:
			#			if ela.attrib['id'] == "descText":
			#				el = ela
			if el != "":
				cleaned = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(el).decode('utf-8')))
				#for className in self.badClasses:
				#	for el in cleaned.find_class(className):
				#		el.getparent().remove(el)
				#print(cleaned.text_content())
				#return cleaned.text_content()
				for videodownload in cleaned.find_class("downloadvideoico"):
					videodownload.drop_tree()
				for style in cleaned.findall(".//style"):
					style.drop_tree()
				for br in cleaned.findall(".//br"):
					if br.tail:
						br.tail="\n"+br.tail
					else:
						br.tail="\n"
				for p in cleaned.findall('.//p'):
					if p.tail:
						p.tail="\n"+p.tail
					else:
						p.tail="\n"
				to_return = cleaned.text_content()+"\n"
				toadd = ""
				if introels is not None:
					for introel in introels:
						toadd += introel.text_content()+"\n"
				to_return = toadd + to_return

				to_return = re.sub('\r\n*', '\n', to_return)
				to_return = re.sub('\n\n\n*', '\n', to_return)
				#print(to_return)
				to_return = to_return.strip('\n \t')
				return to_return

			else:
				return ""

	def get_date(self):
		dateEl = self.doc.find_class('article_date')
		if len(dateEl)==0:
			dateEl = self.doc.find_class('date')
		dateBlah = dateEl[0].text_content().strip('\r\n	 ')
		if re.match("^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$", dateBlah):
			self.date = time.strftime('%Y-%m-%d', time.strptime(dateBlah, "%d.%m.%Y"))
		else:
			dateBlah = re.sub('.*([0-9]{2}\.[0-9]{2}\.[0-9]{4} [0-9]{2}:[0-9]{2}).*', '\\1', dateBlah)
			self.date = time.strftime('%Y-%m-%dT%H:%M', time.strptime(dateBlah, "%d.%m.%Y %H:%M"))

	def url_to_aid(self, url):
		if self.rePagecode.search(url):
			idsofar = self.rePagecode.search(url).groups()[0]
			if len(idsofar) > 4:
				return idsofar
			else:
				idsofar = self.rePagecode2.search(url).groups()[0]
				return idsofar
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperAKumukia(Scraper):
	domain = "kumukia.ru"
	prefix = "kumukia"
	dateRe = re.compile("[0-9]{2}\.[0-9]{2}\.[0-9]{4}")

	def scraped(self):
		self.get_content(encoding="utf-8")
		#self.doc.find_class("qa-content"):		
		for el in self.doc.xpath("//p[@class='href']"):
			el.getparent().remove(el)
		#print(lxml.html.clean.clean_html(self.doc).text_content())
		if len(self.doc.find_class("qa-content"))>0:
			contentElement = self.doc.find_class("qa-content")[0]
		elif len(self.doc.xpath("//div[@id='qa-content']"))>0:
			contentElement = self.doc.xpath("//div[@id='qa-content']")[0]
		else:
			contentElement = self.doc.xpath("//div[@id='qa-content']")[0]

		### get rid of trailing junk ###
		found = False
		for el in contentElement:
			if el.attrib.get("class")=='qa-info' or found:
				#print(el)
				found = True
				el.drop_tree()
			if el.tag=="style":
				el.drop_tree()
		if self.source is not None:
			self.source.title = self.doc.xpath("//p[@class='title']")[0].text_content()
		try:
			#datetext = self.doc.find_class("qa-info")[0].decode('utf-8')
			datetext = self.doc.xpath("//div[@class='qa-info']")[0].text_content()
			#print("findall", re.findall("[0-9]{2}\.[0-9]{2}\.[0-9]{4}", datetext))
			#print("dateRe", self.dateRe.findall(datetext))
			date = self.dateRe.findall(datetext)[0]
			#print(date)
			self.date = time.strftime('%Y-%m-%d', time.strptime(date, "%d.%m.%Y"))
		except:
			self.date = None

		content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(contentElement).decode('utf-8'))).text_content().strip()
		return content
	
	def url_to_aid(self, url):
		link = urllib.parse.unquote(url)
		aid = link.split('.ru/')[1].replace(r'.html','')
		if aid is not None:
			return aid
		else:
			return sha1(link.encode('utf-8')).hexdigest()


class ScraperKumukiaAdab(Scraper):
	domain = "kumukia.ru/adabiat"
	prefix = "kumukia.adabiyat"
	aidRe = re.compile("work=([0-9]{1,3})\&page=([0-9]{1,3})")
	notRus = ['46', '45']
	noLang = ['60', '62', '63', '34']
	defRus = ['59', '32']

	def scraped(self):
		self.get_content(encoding="windows-1251")
		#self.doc.find_class("qa-content"):		
		(work, page) = self.work_and_page(self.url)

		root = E.HTML(self.doc)

		if work in self.notRus:
			rus = root.xpath("//*[@class='rus']")
			if rus:
				rus[0].attrib['class']='kum'
			qum = root.xpath("//*[@class='qum']")
			if qum:
				qum[0].attrib['class']='kum'
		elif work in self.noLang:
			root.attrib['class'] = 'kum'	
		if work in self.defRus:
			for kum in root.xpath("//*[@class='kum']"):
				kum.attrib['class']='rus'

		# get rid of menus
		for el in self.doc.xpath("//div[@class='topmenu']"):
			el.getparent().remove(el)
		# get rid of Russian text
		for el in self.doc.xpath("//*[@class='rus']"):
			el.getparent().remove(el)

		#for el in self.doc.xpath("//a"):
		#	el.getparent().remove(el)
		#print(lxml.html.clean.clean_html(self.doc).text_content())
		#contentElement = self.doc.find_class("qa-content")[0]

		#kumykText = self.doc.xpath("//*[@class='kum']")
		#if kumykText:
		#	contentElement = kumykText[0]
		#else:
		#	# some pages just have class='rus'
		#	return False

		contentElement = E.HTML()
		# the good stuff all seems to be in <p/td class='kum'> nodes.
		# sometimes there's <pre class='kum'> within other class='kum' nodes;
		# so we need to be careful and just choose the good stuff
		for kumykText in self.doc.xpath("//p[@class='kum']|//td[@class='kum']"):
			contentElement.append(kumykText)
		#if contentElement is None:
		#	# some pages just have class='rus'
		#	return False

		#contentElement = self.doc

		### get rid of trailing junk ###
		found = False

		if self.source is not None:
			h3 = self.doc.xpath("//h3")
			if h3:
				self.source.title = h3[0].text_content()
			moreTitle = self.doc.xpath("//*[@class='title']")
			if moreTitle:
				if self.source.title != "":
					self.source.title += " - "
				self.source.title += moreTitle[0].text_content()
		self.date = None

		content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(contentElement).decode('utf-8'))).text_content().strip()
		return content
	
	def work_and_page(self, url):
		matches = self.aidRe.search(url)
		if matches:
			(work, page) = (matches.group(1), matches.group(2))
			return (work, page)
		else:
			return (None, None)

	def url_to_aid(self, url):
		(work, page) = self.work_and_page(url)
		if work and page:
			aid = "w%s+p%s" % (work, page)
		else: aid = None

		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperErkinli(Scraper):
	domain = "www.radioerkinli.com"
	prefix = "erkinli"
	badClasses = ['mediaplayer audioplayer','cannot-play j_errorContainer', 'downloadlinkstatic', 'playlistlink', 'expandMediaClose']
	
	def scraped(self):
		self.get_content()
		contentFinal = ""
		for zoomMeTag in self.doc.find_class("zoomMe"):
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(zoomMeTag).decode('utf-8')))
			if len(content.text_content()) > len(contentFinal.text_content() if contentFinal != "" else contentFinal):
				contentFinal = content
		for className in self.badClasses:
			for el in contentFinal.find_class(className):
				el.getparent().remove(el)
		return contentFinal.text_content().strip()

	def url_to_aid(self, url):
		if 'archive/news' in url:
			aid = url.split('?id=')[1]
		else:
			urlSplit = re.findall('[0-9]{6,8}\.html$', url)
			if len(urlSplit):
				aid = urlSplit[0].replace('.html','')
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()

class ScraperKrymr(Scraper):
	domain = "ktat.krymr.com"
	prefix = "krymr"
	badClasses = ['mediaplayer audioplayer','cannot-play j_errorContainer', 'downloadlinkstatic', 'playlistlink', 'expandMediaClose']
	
	def scraped(self):
		self.get_content()
		contentFinal = ""
		for zoomMeTag in self.doc.find_class("zoomMe"):
			content = lxml.html.document_fromstring(lxml.html.clean.clean_html(lxml.html.tostring(zoomMeTag).decode('utf-8')))
			if len(content.text_content()) > len(contentFinal.text_content() if contentFinal != "" else contentFinal):
				contentFinal = content
		for className in self.badClasses:
			for el in contentFinal.find_class(className):
				el.getparent().remove(el)
		return contentFinal.text_content().strip()

	def url_to_aid(self, url):
		if 'archive/news' in url:
			aid = url.split('?id=')[1]
		else:
			urlSplit = re.findall('[0-9]{6,8}\.html$', url)
			if len(urlSplit):
				aid = urlSplit[0].replace('.html','')
		if aid is not None:
			return aid
		else:
			return sha1(url.encode('utf-8')).hexdigest()
	
