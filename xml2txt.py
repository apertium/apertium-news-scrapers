#!/usr/bin/env python3
#import xml.etree.ElementTree as etree
import os
import sys
import re
from lxml import etree
import argparse
import codecs
import rlcompleter
import subprocess

def totxt(fn):
	#xmlFile = re.compile(".*\.xml$")
	#if xmlFile.match(fn):
	if os.path.isfile(fn):
		fileHandle = open (fn,"r" )
		lineList = fileHandle.readline()
		fileHandle.close()
		root = etree.parse(fn).getroot()
		attributes = root.attrib
		lang=attributes.get("language")
		for item in root.getiterator("{http://apertium.org/xml/corpus/0.9}entry"):
			if args['sentence'] is not False: #split by sentence
				itemtxt=str(item.text)
				tosplit=itemtxt.replace('   ',' ')
				if lang == "eng" or lang == "en" or lang == "rus" or lang == "ru" or lang == "hye" or lang == "hy":
                                        py2output = subprocess.check_output(['python', 'getnltk.py', tosplit, lang])
                                        py2output=(str(py2output,'utf-8'))
				else:
					print("language not supported")
					sys.exit("language not supported")
				if args['output_file'] is not None:
						output.write(item.attrib['title']+'\n'+py2output)
				else:
					sys.stdout.write((item.attrib['title']+'\n'+py2output))
			else: #split by paragraph (default)
				if args['output_file'] is not None:
					output.write((item.attrib['title']+'\n'+item.text+'\n\n'))
				else:
					sys.stdout.write((item.attrib['title']+'\n'+item.text+'\n\n'))

def reattach(sentences):
    punctuation = ('.','!','?')
    previous = ''
    for sentence in sentences:
        if sentence not in punctuation:
            previous = sentence
        else:
            yield previous + sentence
            previous = ''
    if previous:
        yield previous + "\n"


#argparser
parser = argparse.ArgumentParser(description='xml to txt script')
parser.add_argument('corpus_dir', metavar='i', help='corpus directory (input)')
parser.add_argument('-o','--output_file', help='name of output_file', required=False)
parser.add_argument('-s', '--sentence', action='store_true', help="Splits corpus into sentences (only for trained languages; see http://wiki.apertium.org/wiki/Sentence_segmenting for more info)")



args = vars(parser.parse_args())

if args['output_file'] is not None:
	output = open(args['output_file'], 'w')



#if (args['corpus_dir'])[-4:] == ".xml": #checks if user entered an xml file
if os.path.isfile(args['corpus_dir']): #checks if user entered an xml file
	totxt(args['corpus_dir'])
	if args['output_file'] is not None:
		filename=args['corpus_dir'][args['corpus_dir'].rfind('/')+1:]
		print("Adding content from "+filename)
		print("Done.")
#else: #if directory
elif os.path.isdir(args['corpus_dir']):
	os.chdir(args['corpus_dir'])
	files = os.listdir('.')
	for fn in files:
		filename=fn
		if args['output_file'] is not None:
			print("Adding content from "+fn)
		totxt(fn)
	if args['output_file'] is not None:
		print("Done.")

		

if args['output_file'] is not None:
	output.close()


