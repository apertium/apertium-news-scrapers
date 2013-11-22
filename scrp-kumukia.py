#!/usr/bin/env python3

import requests, lxml, lxml.html

debug = False

def _url(path):
  return "http://kumukia.ru/{}".format(path)

base = _url("cat-qumuq.html")

page = lxml.html.fromstring(requests.get(base).text)

cats = []

for link in page.findall(".//a"):
  for k, v in link.items():
    if k == "href" and v.startswith("cat-"):
      cats.append(_url(v))

print("Found {} categories".format(len(cats)))

links = []

for cat in cats:
  page = lxml.html.fromstring(requests.get(cat).text)
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
