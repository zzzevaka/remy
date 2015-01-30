#!/usr/bin/python

import sys
import os
import json
from debug import Except
import logging
sys.path.insert(0, os.path.expanduser('~/Dropbox/Reminder/database'))
from db import DBconnect
from PyQt4 import QtCore
import os

class Word():
	
	def __init__ (self, word, translate, weight = 1, id = None):
		self.id = id
		self.word = word
		if type(translate) == list:
			self.translate = translate
		elif type(translate) == str:
			self.translate = translate
		
		self.weight = weight
		
		
	def toList (self):
		return {'word' : self.word, 'translate' : self.translate, 'weight' : self.weight}

	def __str__ (self):
		return 'word : {}, translate : {}, weight : {}'.format(self.word, self.translate, self.weight)

	def __getitem__ (self, attr):
		return getattr(self, attr)

class DictionaryUpdater (QtCore.QObject):
	@Except
	def __init__ (self, db, parent = None):
		logging.info('Start dictionary constructor')
		QtCore.QObject.__init__ (self, parent)
		
		self.file_path = os.path.expanduser('~/.reminder/dictionary.json')
		file = open (self.file_path, 'r')
		logging.info('Has been opened a file {}'.format(self.file_path))
		self.db = db
		self.db.dictionary_updated.connect(self.updateFile)
		self.db.query("DELETE FROM dictionary WHERE 1=1")
		logging.info('Has been cleared DB table dictionary')
		for line in file:
			try:
				tmp_word = json.loads(line)
			except ValueError as a:
				logging.warning('Can\'t add a word from file: {}'.format(line))
				continue
			if 'weight' in tmp_word:
				self.db.addWord( Word (tmp_word['rus'], tmp_word['eng'], tmp_word['weight']) )
			else:
				self.db.addWord( Word (tmp_word['rus'], tmp_word['eng']) )
		file.close()
	
	@Except
	@QtCore.pyqtSlot()
	def updateFile (self):
		file = open (self.file_path, 'w')
		for row in self.db.getAllDictionary():
			tmp_str = '{'
			tmp_str += '"eng" : "{0}", "rus" : {2}, "weight" : {1}'.format(row['word'], row['weight'], row['translate'])
			tmp_str += '}\n'
			logging.info('Write to dictionary file: {}'.format(tmp_str))
			file.write(tmp_str.replace("'", '"'))
			logging.info('update dictionary: {}'.format(row))
		file.close()
	
