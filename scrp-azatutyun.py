#!/usr/bin/env python3
import http.client
import hashlib
import os.path
import urllib
import sys
import re

domain = "www.azatutyun.am"
contents = ""


if not os.path.exists('./.cache'):
    os.makedirs('./.cache')


def get_article_content(source):
	return re.findall('<div class="zoomMe">(.*?)</div>', source, flags=re.DOTALL|re.MULTILINE)[0]

def get_contents(url, encoding):
    while True:
        try:
            url_md5 = hashlib.md5(url.encode()).hexdigest()
            if(os.path.isfile('./.cache/' + url_md5)):
                f = open('./.cache/' + url_md5, 'rb')
                contents = f.read().decode('utf-8')
                f.close()
                return contents
            else:
                conn = http.client.HTTPConnection(domain, 80, timeout=60)
                conn.request("GET", url)
                res = conn.getresponse()
                if res.status != 200:
                    print(res.status, res.reason)
                contents = res.read().decode(encoding)
                f = open('./.cache/' + url_md5, 'wb')
                f.write(contents.encode('utf-8'))
                f.close()
                conn.close()
                return contents
        except:
            continue
        break


def get_article_ids(start_date, end_date): #dot separated. e.g: D.M.Y
	print("get_article_ids("+start_date+", "+end_date+")")

	search_url = "http://www.azatutyun.am/search/?st=article&k=*&df="+start_date+"&dt="+end_date+"&ob=rel&p="
	article_ids = []
	#Get the search_url page, extract links. if there's a "next page" link, follow it, else return the ids.
	keep_going = True
	page_counter = 1
	while keep_going:
		local_search_url = search_url + str(page_counter)
		page = get_contents(local_search_url, 'utf-8')
		raw_link_lines = re.findall('<div class=\"searchResultItem\">(.*?)</div>', page)

		for line in raw_link_lines:
			article_ids.append(re.findall('\'(/content/[\w]+/[\d]+\.html)\'', line)[0])

		if ">Հաջորդը</a>" not in page:
			keep_going = False
		page_counter = page_counter + 1

	return article_ids



links = get_article_ids("20.11.12", "20.12.12")
for link in links:
	pass
	#print(get_contents(link, 'utf-8'))
source = get_contents(links[0], 'utf-8')
print(get_article_content(source))
