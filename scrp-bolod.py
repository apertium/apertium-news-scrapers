#!/usr/bin/env python3

import http.client
import hashlib
import os.path
import urllib
import sys
from scrapers import ScraperBolod
from scraper_classes import Source, Writer
import signal

domain = "www.bolod.mn"
article_url = "/modules.php?name=News&nID="
contents = ""

if not os.path.exists('./.cache'):
    os.makedirs('./.cache')

def get_between(strSource, strStart, strEnd): #get first string between 2 other strings
    try:
        parse = strSource.split(strStart, 2)[1]
        parse = parse[:parse.find(strEnd)]
    except:
        parse = None
    return parse

def get_between_all(strSource, strStart, strEnd): #get all the strings between the 2 strings
    list = []
    start = 0
    word = get_between(strSource, strStart, strEnd)
    while (word != None):
        list.append(word)
        start = strSource.find("".join((strStart, word, strEnd)))
        strSource = strSource[start+len("".join((strStart, word, strEnd))):]
        word = get_between(strSource, strStart, strEnd)
    return list

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

def get_cats(): #get all the category ids from the website
    contents = get_contents("/index.php", 'utf-8')
    categories = get_between_all(contents, 'modules.php?name=News&catid=', '"')
    outlist = []
    for element in categories:
        if element not in outlist:
            outlist.append(element)
    return outlist

def get_articles(cat_id, pg): #get all the article ids from specific category id (and page #)
    contents = get_contents("/modules.php?name=News&catid=" + cat_id + "&pg=" + str(pg), 'utf-8')
    return get_between_all(contents, '<td><b><a href="modules.php?name=News&nID=', '</a></b></td>')

def get_urls(): #get all the formatted article URLs
    cats = get_cats()
    article_ids = []
    for cat_id in cats:
        for article_info in get_articles(cat_id, 1):
            article_info = article_info.split('">')
            yield article_url + article_info[0], article_info[1].replace('\t', '').strip()
        limit = contents.count("&pg=")
        if limit > 1:
            for i in range(2, limit + 1):
                for article_info in get_articles(cat_id, i):
                    article_info = article_info.split('">')
                    yield article_url + article_info[0], article_info[1].replace('\t', '').strip()

def main():
    conn = http.client.HTTPConnection("www.bolod.mn")
    ids = None
    root = None
    w = Writer()
    
    def term_handler(sigNum, frame):
        print("\nReceived a SIGTERM signal. Closing the program.")
        w.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    
    try:
        for (url, title) in get_urls():
            try:
                source = Source(url, title=title, scraper=ScraperBolod, conn=conn)
                #source.out_content = source.scraper.scraped()
                #print(source.out_content)
                source.makeRoot("./", ids=ids, root=root)
                source.add_to_archive()
                if ids is None:   # ighf not ids:
                    ids = source.ids
                if root is None:  # if not root:
                    root = source.root
            except Exception as e:
                sys.stdout.write(str(e))
    except KeyboardInterrupt:
        print("\nReceived a keyboard interrupt. Closing the program.")
    w.close()
    conn.close()

main()
