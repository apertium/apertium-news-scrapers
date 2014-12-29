#!/usr/bin/env python3

import http.client
import html.parser
import hashlib
import os.path
import urllib
import sys
import signal
from scrapers import ScraperOlloo
from scraper_classes import Source, Writer

domain = "www.olloo.mn"
article_url = "/modules.php?name=News&file=print&sid="
contents = ""
h = html.parser.HTMLParser()

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

def get_list_urls(): #get all the urls of the pages with links to articles
    contents = get_contents("/modules.php?name=Stories_Archive", 'cp1251')
    contents = contents.replace('V', 'Ү')
    contents = contents.replace('v', 'ү')
    contents = contents.replace('Є', 'Ө')
    contents = contents.replace('є', 'ө')
    return get_between_all(contents, '<li><a href="modules.php?', 'l=')

def get_articles(year, month): #get all the article ids from specific category id (and page #)
    while True:
        try:    
            contents = get_contents("/modules.php?name=Stories_Archive&sa=show_month&year=" + year + "&month=" + month, 'cp1251')
            return get_between_all(contents, 'modules.php?name=News&amp;file=article&amp;sid=', '</a></td>')
        except:
            continue
        break

def get_urls(): #get all the formatted article URLs
    params_list = get_list_urls()
    for params in params_list:
        year = get_between(params, "&year=", "&month=")
        month = get_between(params, "&month=", "&month_")
        info = get_articles(year, month)
        for article_info in info:
            article_info = article_info.split('">')
            yield article_url + article_info[0], h.unescape(article_info[1])

def main():
    conn = http.client.HTTPConnection("www.olloo.mn")
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
                source = Source(url, title=title, scraper=ScraperOlloo, conn=conn)
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
