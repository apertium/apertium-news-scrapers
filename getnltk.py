#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nltk
from nltk import *
import argparse
from urllib import urlopen



textt='' #for hye

#argparse
parser = argparse.ArgumentParser(description='xml to txt script')
parser.add_argument('txt', metavar='t', help='text to input')
parser.add_argument('lang', metavar='l', help='language')
args = vars(parser.parse_args())
text = str(args['txt'])
if args['lang'] == "eng" or args['lang'] == "en":
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
elif args['lang'] == "rus"or  args['lang'] == "ru":
	raw1=urlopen('http://danielhonline.com/ruscorpus.html').read()#corpus
	raw = nltk.clean_html(raw1) 
	trainer = nltk.tokenize.punkt.PunktTrainer(raw) 
	trainer.INCLUDE_ALL_COLLOCS = True 
	trainer.INCLUDE_ABBREV_COLLOCS = True
	params = trainer.get_params()
	trainer.train(raw) 
	sbd = PunktSentenceTokenizer(params) 
	for sentence in sbd.sentences_from_text(text, realign_boundaries=True): 
		print sentence
elif args['lang'] == "hye" or args['lang'] == "hy":
	some_text = text.replace('։', ':')
	
	armenian_punkt_vars = nltk.tokenize.punkt.PunktLanguageVars
	armenian_punkt_vars.sent_end_chars=('!', ':', '։', '?')
	trainer = nltk.tokenize.punkt.PunktTrainer(textt, armenian_punkt_vars)
	params = trainer.get_params()

	sbd = nltk.tokenize.punkt.PunktSentenceTokenizer(params)
	for sentence in sbd.sentences_from_text(some_text):
		sentence1=sentence.replace(":","։")
		print sentence1
if args['lang'] == "eng" or args['lang'] == "en":
	print '\n'.join(sent_detector.tokenize(text.strip()))
