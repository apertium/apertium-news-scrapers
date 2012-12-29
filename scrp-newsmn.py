#!/usr/bin/env python3

from datetime import date
import lxml.html
import http.client

startDate = date(2011, 12, 1)
endDate = date(2011, 12, 2)

urlTemplate = "/archive.shtml?q=&from=%s&to=%s&sortBy=NEWEST&page=%s"

articles = []

def getPage(conn, url):
    conn.request("GET", url)
    res = conn.getresponse()
    if res.status != 200:
        print(url, res.status, res.reason)
        return
    contents = res.read().decode('utf-8')
    doc = lxml.html.fromstring(contents)
    return doc

def printArticles(articlesData, fileName, display=False):
    #with open(fileName, 'w',encoding='utf-8') as thefile:
    #    for (title, url) in articlesData:
    #        thefile.write("%s, %s\n" % (title, url))
    for (title, url) in articlesData:
        print(title, url)
        
def main(startDate, endDate):
    conn = http.client.HTTPConnection("archive.news.mn")
    url = urlTemplate % (startDate.isoformat(),endDate.isoformat(),1)
    doc = getPage(conn, url)
    numTag = str(lxml.html.tostring(doc.find_class("search-result")[0]))
    numArticles = int(numTag[numTag.find('/')+2:numTag.find("</")])
    
    for i in range(1,int(numArticles/20)+2) :
        url = urlTemplate % (startDate.isoformat(),endDate.isoformat(),i)
        doc = getPage(conn, url)
        divTags = doc.find_class("bd-list-title")
        if len(divTags) is 0:
            break
        for divTag in divTags:
            for article in divTag:
                title = article.text
                url = article.attrib["href"]
                articles.append((title, url))
    assert numArticles is len(articles) #Ensure correct number of articles have been retrieved
    print("%s Articles scraped from %s to %s" % (str(len(articles)), startDate, endDate))
    printArticles(articles,"test.txt",display=True)
        
main(startDate, endDate)
