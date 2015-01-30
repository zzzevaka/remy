#!/usr/bin/env python

import sys
import os
import sqlite3
import logging
#~ import dictionary
from PyQt4 import QtCore
from debug import Except


class DBconnect(QtCore.QObject):
	@Except
	def __init__ (self, parent = None):
		logging.info('Create new DB connection')
		QtCore.QObject.__init__(self, parent)
		# PATH TO DATABASE FILE
		path = os.path.expanduser('~/.reminder/')
		db = '{}database.db'.format(path)
		# CREATE DIR IF DOESN'T EXISTS
		if not os.path.exists(os.path.expanduser(path)):
			os.makedirs(os.path.expanduser('~/.reminder/'))
			logging.info('Dir {} has been made'.format(path))
			
		# CONNECT
		logging.info('Connect to slite3 - {}'.format(db))
		self.connection = sqlite3.connect(db)
		self.cursor = self.connection.cursor()
		# NAMES OF TABLES
		self.notification_table = 'notification'
		self.dictionary_table = 'dictionary'
		# CREATE TABLES IF DON'T EXISTS
		self.createNotificationTable()
		self.createDictionaryTable()
		logging.info('DBconnect constructor has been finished')
	
	def __del__ (self):
		self.connection.close()
		#~ logging.info('Has been closed DB conenction')
	
	#######################################
	# SIGNALS
	#######################################
	table_changed = QtCore.pyqtSignal()
	delete_notification = QtCore.pyqtSignal(int)
	add_notification = QtCore.pyqtSignal(int, int, str)
	dictionary_updated = QtCore.pyqtSignal()
	
	def query(self, string):
		try:
			logging.info('DB query executing: {}'.format(string))
			self.cursor.execute(string)
			self.connection.commit()
			return self.cursor
		except Exception as e:
			logging.error('An SQL error occurred: {}'.format(e.args[0]))
			raise
	
	@Except	
	def createNotificationTable (self):
		q = '''CREATE TABLE IF NOT EXISTS {0}(
					notif_id INTEGER PRIMARY KEY NOT NULL,
					text VARCHAR(255) NOT NULL,
					date DATETIME,
					status BOOLEAN);
		'''.format(self.notification_table)
		self.query(q)
		logging.info('Has been created new notification table')
	
	@Except
	@QtCore.pyqtSlot(str, str)
	def addNotification (self, dateTime, text):
		q = "INSERT INTO {0} (text, date, status) VALUES ('{1}', datetime('{2}'), 0)".format(self.notification_table, text, dateTime)
		self.query(q)
		self.table_changed.emit()
		notif_id = self.query('SELECT MAX(notif_id) FROM {0}'.format(self.notification_table)).fetchone()[0]
		secs_to_event = QtCore.QDateTime.currentDateTime().secsTo(QtCore.QDateTime.fromString(dateTime, 'yyyy-MM-dd hh:mm:ss'))
		self.add_notification.emit(notif_id, secs_to_event, text)
		logging.info('Has been added notification to DB')
	
	@Except
	@QtCore.pyqtSlot(int)		
	def deleteNotificationById(self, id_int):
		q = "DELETE FROM {0} WHERE notif_id == {1}".format(self.notification_table, id_int)
		self.query(q)
		self.table_changed.emit()
		self.delete_notification.emit(id_int)
		logging.info('Has been removed notification {} from DB'.format(id_int))
		
	@Except
	@QtCore.pyqtSlot(str, str)	
	def deleteNotificationByVal (self, dateTime, text):
		q = "SELECT notif_id FROM {0} WHERE text == '{1}' and date == datetime('{2}')".format(self.notification_table, text, dateTime)
		for x in self.query(q):
			print ("deleteNotificationByVal: id == {}".format(x[0]))
			self.deleteNotificationById(x[0])
			logging.info('Has been removed notification wuth id == {}'.format(x[0]))
	
	@Except
	@QtCore.pyqtSlot(str, str)
	def deactivateNotificationByVal (self, dateTime, text):
		q = "UPDATE {0} SET status = 1 WHERE text == '{1}' and date == datetime('{2}')".format(self.notification_table, text, dateTime)
		self.query(q)
		logging.info('Has been deativated notification by val')
		self.table_changed.emit()

	@Except
	@QtCore.pyqtSlot(int)
	def deactivateNotificationByIndex (self, index):
		q = "UPDATE {0} SET status = 1 WHERE notif_id == {1}".format(self.notification_table, index)
		self.query(q)
		logging.info('Has been deativated notification by id:'.format(index))
		self.table_changed.emit()	
	
	@Except
	def getAllCurrentNotifications (self):
		'''return cursor sqlite3. Can be iterated.
		For example:
		for row in getAllCurrentNotifications():
			print (notif_id = {0}, text = {1}, date = {2}, status = {3})'''
		q = "SELECT * FROM {0} WHERE status == 0 ORDER by date".format(self.notification_table)
		self.query(q)
		#~ logging.info('Has been got notifications')
		tmp = []
		for x in self.cursor:
			tmp.append(x)
		return tmp
			
	
	@Except
	def createDictionaryTable (self):
		q = '''CREATE TABLE IF NOT EXISTS {0}(
				word_id INTEGER PRIMARY KEY NOT NULL,
				word VARCHAR(100) NOT NULL,
				translate VARCHAR(100) NOT NULL,
				weight INTEGER NOT NULL);'''.format(self.dictionary_table)
		self.query(q)
		
	@Except
	@QtCore.pyqtSlot(str, str, int)
	def addWord (self, word):
		#~ if type(translate) == str:
			# PYTHON 2
			#~ word = unicode(word, 'utf-8')
			#~ translate = unicode(translate, 'utf-8')
			# PYTHON 3
			#~ word = word.decode('utf-8')
			#~ translate = translate.decode('utf-8')
		q = '''INSERT INTO {0} (word, translate, weight)
		VALUES ("{1}", "{2}", {3})'''.format(self.dictionary_table, word['word'], word['translate'], word['weight'])
		self.query(q)

	@Except
	def getAllDictionary (self):
		'''return cursor sqlite3. Can be iterated.
		For example:
		for row in getAllCurrentNotifications():
			print (word_id = {0}, word = {1}, translate = {2}, weight = {3})'''
		q = "SELECT * FROM {0} ORDER by word_id".format(self.dictionary_table)
		self.query(q)
		tmp = []
		for x in self.cursor:
			tmp.append({'word' : x[1], 'translate' : x[2], 'weight' : x[3]})
			
		return tmp
		
	@Except
	def getNextWord (self):
		q = "SELECT * FROM {0} ORDER by weight LIMIT 1".format(self.dictionary_table)
		self.query(q)
		for x in self.cursor:
			return {"word_id" : x[0], "word" : x[1].replace("'", '"'), "translate" :  x[2].replace("'", '"'), "weight" : x[3]}

	@Except
	def updateWordHeight (self, word_id, weight):
		q = "UPDATE {0} SET weight = {1} WHERE word_id = {2}".format(self.dictionary_table, weight, word_id)
		self.query(q)
		self.dictionary_updated.emit()
		
