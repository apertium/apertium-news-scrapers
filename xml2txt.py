#!/usr/bin/env python3
#import xml.etree.ElementTree as etree
import os
import sys
import re
from lxml import etree
import argparse
import codecs

def totxt(fn):
	xmlFile = re.compile(".*\.xml$")
	if xmlFile.match(fn):
		
		root = etree.parse(fn).getroot()
		for item in root.getiterator("{http://apertium.org/xml/corpus/0.9}entry"):
			if args['sentence'] is not False: #split by sentence
				itemtxt=str(item.text)
				tosplit=itemtxt.replace('   ',' ')
				if "Ա" and "ա" or "է" or "ի" or "ո" or "ը" in tosplit.decode("utf-8"):
					sentences = re.split('(?<=[:])(\s)?(?=[\u0531-\u0556])?', tosplit)
					if "а" in tosplit:
						sentences = re.split('(?<=[.!?])\s(\s)?[\u0410-\u042F]', tosplit)
				elif "D" or "d" or "F" or "f" or "G" or "g" or "I" or "i" or "J" or "j" or "L" or "l" in tosplit:
					sentences = re.split('(?<=[.!?])\s(?=[A-Z])', tosplit)
				else:
					print("language not supported")
					sys.exit()
				if args['output_file'] is not None and sentences is not None:
					
					output.write((item.attrib['title']+'\n'+('%s' % '\n'.join(map(str, sentences)))+'\n\n').replace("None", ""))
				else:
					sys.stdout.write((item.attrib['title']+'\n'+('%s' % '\n'.join(map(str, sentences)))+'\n\n').replace("None", ""))
			else: #split by paragraph (default)
				if args['output_file'] is not None:
					output.write((item.attrib['title']+'\n'+item.text+'\n\n'))
				else:
					sys.stdout.write((item.attrib['title']+'\n'+item.text+'\n\n'))

#argparser
parser = argparse.ArgumentParser(description='xml to txt script')
parser.add_argument('corpus_dir', metavar='i', help='corpus directory (input)')
parser.add_argument('-o','--output_file', help='name of output_file', required=False)
parser.add_argument('-s', '--sentence', action='store_true')



args = vars(parser.parse_args())

if args['output_file'] is not None:
	output = open(args['output_file'], 'w')



if (args['corpus_dir'])[-4:] == ".xml": #checks if user entered an xml file
	totxt(args['corpus_dir'])
	if args['output_file'] is not None:
		print("Adding content from "+args['corpus_dir'][(args['corpus_dir'].rfind('/'))+1:])
		print("Done.")
else: #if directory
	os.chdir(args['corpus_dir'])
	files = os.listdir('.')
	for fn in files:
		if args['output_file'] is not None:
			print("Adding content from "+fn)
		totxt(fn)
	if args['output_file'] is not None:
		print("Done.")

		

if args['output_file'] is not None:
	output.close()


