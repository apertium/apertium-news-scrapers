#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, lxml, lxml.html

debug = False

def _url(path):
  return "http://kumukia.ru/{}".format(path)


cats = [_url("cat-qumuq.html")]
links = []

for cat in cats:

  page = lxml.html.fromstring(requests.get(cat).text)

  sub_page = page.find(".//div[@id='list-subs']")
  if sub_page is not None:
    for sub in sub_page.findall(".//a"):
      for k, v in sub.items():
        if k == "href" and v.startswith("cat-"):
          if _url(v) not in cats:
            cats.append(_url(v))

  for link in page.findall(".//a"):
    if "title" in link.keys():
      title = link.get("title")
      if title == "–>":
        cats.append(_url(link.get("href")))
    if link.text_content() == "Далее...":
      links.append(_url(link.values()[0]))

if debug:
  for link in links:
    page = requests.get(link)
    if page.status_code != 200:
      print("{} is not reachable...".format(link))

links = list(set(links))
print("Found {} articles...".format(len(links)))

print("\n".join(links))