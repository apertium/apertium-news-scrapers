#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nltk
from nltk import *
import argparse
text=''
parser = argparse.ArgumentParser(description='xml to txt script')
parser.add_argument('txt', metavar='t', help='text to input')
parser.add_argument('lang', metavar='l', help='language')
args = vars(parser.parse_args())
text = str(args['txt'])
if args['lang'] == "eng":
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
elif args['lang'] == "rus":
	sent_detector = nltk.data.load('tokenizers/punkt/russian.pickle')
elif args['lang'] == "hye":
	some_text = text.replace('։', ':')
	
	armenian_punkt_vars = nltk.tokenize.punkt.PunktLanguageVars
	armenian_punkt_vars.sent_end_chars=('!', ':', '։', '?')
	trainer = nltk.tokenize.punkt.PunktTrainer(text, armenian_punkt_vars)
	params = trainer.get_params()

	sbd = nltk.tokenize.punkt.PunktSentenceTokenizer(params)
	for sentence in sbd.sentences_from_text(some_text):
		sentence1=sentence.replace(":","։")
		print sentence1
if args['lang'] == "eng" or args['lang'] == "rus":
	print '\n'.join(sent_detector.tokenize(text.strip()))
