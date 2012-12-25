#!/usr/bin/env python3

#import xml.etree.ElementTree as etree
import os
import sys
import re
from lxml import etree
import argparse

#argparser
parser = argparse.ArgumentParser(description='xml to txt script')
parser.add_argument('-i','--corpus_dir', help='corpus directory (input)', required=True)
parser.add_argument('-o','--output_file', help='name of output_file', required=True)
parser.add_argument('-s','--sentence', help='split by sentence', required=False)

args = vars(parser.parse_args())

output = open(args['output_file'], 'w')
os.chdir(args['corpus_dir'])
files = os.listdir('.')

xmlFile = re.compile(".*\.xml$")

for fn in files:
	if xmlFile.match(fn):
		print("Adding content from "+fn)
		root = etree.parse(fn).getroot()
		for item in root.getiterator("{http://apertium.org/xml/corpus/0.9}entry"):
			output.write(item.attrib['title']+'\n'+item.text+'\n\n')

output.close()
print("Done.")
