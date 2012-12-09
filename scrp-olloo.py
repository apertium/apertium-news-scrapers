#!/usr/bin/env python3

import http.client
import urllib
import sys

article_url = "http://www.olloo.mn/modules.php?name=News&file=print&sid="
contents = ""

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

def get_list_urls(): #get all the urls of the pages with links to articles
    conn = http.client.HTTPConnection("www.olloo.mn", 80, timeout=60)
    conn.request("GET", "/modules.php?name=Stories_Archive")
    res = conn.getresponse()
    if res.status != 200:
        print(res.status, res.reason)
    contents = res.read().decode('cp1251')
    return get_between_all(contents, '<li><a href="modules.php?', 'l=')

def get_article_ids(year, month): #get all the article ids from specific category id (and page #)
    while True:
        try:    
            conn = http.client.HTTPConnection("www.olloo.mn", 80, timeout=60)
            params = urllib.parse.urlencode({'name': 'Stories_Archive', 'sa': 'show_month', 'year': year, 'month': month})
            conn.request("GET", "/modules.php?" + params)
            res = conn.getresponse()
            if res.status != 200:
                print(res.status, res.reason)
            contents = res.read().decode('cp1251')
            return get_between_all(contents, 'modules.php?name=News&amp;file=print&amp;sid=', '"')
        except:
            continue
        break
        

def get_urls(): #get all the formatted article URLs
    params_list = get_list_urls()
    for params in params_list:
        year = get_between(params, "&year=", "&month=")
        month = get_between(params, "&month=", "&month_")
        current_article_ids = get_article_ids(year, month)
        for article_id in current_article_ids:
            yield article_url + article_id


for url in get_urls():
    print(url)

