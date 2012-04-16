#!/usr/bin/env python
import xml.etree.ElementTree as etree
try: import urllib.request as urllib # py3
except: import urllib # py2

def parse_rss(url):
	ns = ""
	out = {}
	
	rss = etree.parse(urllib.urlopen(url)).getroot()
	if len(rss.tag.split("}")) > 1:
		ns = rss.tag.split("}")[0] + "}"
	
	if ns == "{http://www.w3.org/2005/Atom}":
		for item in rss.getiterator(ns + "entry"):
			out[item.find(ns + "title").text] = item.find(ns + "link").attrib['href']

	else:
		for item in rss.getiterator(ns + "item"):
			out[item.find(ns + "title").text] = item.find(ns + "link").text
	
	return out

if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1:
		for k, v in parse_rss(sys.argv[1]).items():
			print("%s: %s" % (k, v))
	else:
		print("Usage: %s url" % sys.argv[0])

