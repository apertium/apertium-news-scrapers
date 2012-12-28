#!/usr/bin/env python3
#import xml.etree.ElementTree as etree
import os
import sys
import re
from lxml import etree
import argparse
import codecs
import rlcompleter

def totxt(fn):
	xmlFile = re.compile(".*\.xml$")
	if xmlFile.match(fn):
		fileHandle = open (fn,"r" )
		lineList = fileHandle.readline()
		fileHandle.close()
		lang=str(lineList)[lineList.__len__()-6:lineList.__len__()-3] # 3-letter iso code of language of corpus
		root = etree.parse(fn).getroot()
		for item in root.getiterator("{http://apertium.org/xml/corpus/0.9}entry"):
			if args['sentence'] is not False: #split by sentence
				itemtxt=str(item.text)
				#print(item)
				tosplit=itemtxt.replace('   ',' ')
				if lang == "eng":
					sentences = re.split('(?<![A-Z])(?<!([A-Z][a-z]\.)|(Mr|St|Ms|Rd|of|rs)\.)(?<![A-Z].)(?<=[.!?])\s(?=[A-Z])', tosplit)
				elif lang == "hye":
					sentences = re.split('(?<=[:])(\s)?(?=[\u0531-\u0556])?', tosplit)
				elif lang == "rus" or lang == "kir" or lang == "khk":
					sentences = re.split('(?<![\u0410-\u042F])([.!?])(?=(\s)?(\s)?[\u0410-\u042F]|[\u04E8]|["]|[\u201C]|![0-9])', tosplit.strip())
                                        #sentences=[]
                                        #for a in aaa:
                                        #     sentences.append(a.strip())
				



				else:
					print("language not supported")
					sys.exit("language not supported")
				if args['output_file'] is not None:
					
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
		filename=args['corpus_dir'][args['corpus_dir'].rfind('/')+1:]
		print("Adding content from "+filename)
		print("Done.")
else: #if directory
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


