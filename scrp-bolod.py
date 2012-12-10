#!/usr/bin/env python3

import http.client
import hashlib
import os.path
import urllib
import sys

domain = "www.bolod.mn"
article_url = "http://www.bolod.mn/modules.php?name=News&nID="
contents = ""

conn = http.client.HTTPConnection(domain, 80, timeout=60)

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
    url_md5 = hashlib.md5(url.encode()).hexdigest()
    if(os.path.isfile('./.cache/' + url_md5)):
        f = open('./.cache/' + url_md5, 'rb')
        contents = f.read().decode('utf-8')
        f.close()
        return contents
    else:
        conn.request("GET", url)
        res = conn.getresponse()
        if res.status != 200:
            print(res.status, res.reason)
        contents = res.read().decode(encoding)
        f = open('./.cache/' + url_md5, 'wb')
        f.write(contents.encode('utf-8'))
        f.close()
        return contents

def get_cats(): #get all the category ids from the website
    contents = get_contents("/index.php", 'utf-8')
    return get_between_all(contents, '&raquo;  <a href="modules.php?name=News&catid=', '">')

def get_articles(cat_id, pg): #get all the article ids from specific category id (and page #)
    contents = get_contents("/modules.php?name=News&catid=" + cat_id + "&pg=" + str(pg), 'utf-8')
    return get_between_all(contents, '<td><b><a href="modules.php?name=News&nID=', '</a></b></td>')

def get_urls(): #get all the formatted article URLs
    cats = get_cats()

    article_ids = []
    for cat_id in cats:
        for article_info in get_articles(cat_id, 1):
            article_info = article_info.split('">')
            yield article_url + article_info[0], article_info[1]
        limit = contents.count("&pg=")
        if limit > 1:
            for i in range(2, limit + 1):
                for article_info in get_articles(cat_id, i):
                    article_info = article_info.split('">')
                    yield article_url + article_info[0], article_info[1]

'''
for url, title in get_urls():
    print([url, title])
'''
