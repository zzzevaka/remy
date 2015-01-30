#!/usr/bin/env python

import sys
import logging
import json
#~ from db import DBconnect
from debug import Except
from PyQt4 import QtGui, QtCore

class Notification (QtGui.QWidget):
	
	@Except
	def __init__ (self, db, index, timer, text, parent = None):
		logging.info('start a notification constructor')
		QtGui.QWidget.__init__(self, parent)
		
		# self.index = index
		self.label = QtGui.QLabel(text)
		self.label.setAlignment(QtCore.Qt.AlignCenter);
		self.button = QtGui.QPushButton('OK')
		# A counter of attempts to translate a word
		self.attempt = 0
		
		self.center()
		self.resize(300,100)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		
		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(True)
		if (timer < 0):
			timer = 0
		self.timer.setInterval(1000 * timer)
		self.timer.timeout.connect(self.show)
		
		###################################
		# DATABASE
		###################################
		self.db_conn = db
		
		###################################
		# GET WORD TO TRANSLATE
		###################################
		word_tmp_hash = self.db_conn.getNextWord()
		logging.info("WORD TMP HASH: {}".format(word_tmp_hash))
		self.word_id = word_tmp_hash['word_id']
		self.word = json.loads(word_tmp_hash['word'])
		self.translate = json.loads(word_tmp_hash['translate'])
		self.word_height = word_tmp_hash['weight']
		self.db_conn.updateWordHeight(self.word_id, self.word_height + 1)
		
		###################################
		# WORD WIDGETS
		###################################
		self.word_lbl = QtGui.QLabel(self.word[0])
		self.tr_field = QtGui.QLineEdit()
		
		###################################
		# LAYOUT
		###################################
		tr_layout = QtGui.QHBoxLayout()
		tr_layout.addWidget(self.word_lbl)
		tr_layout.addWidget(self.tr_field)
		
		###################################
		# MAIN LAYOUT
		###################################
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.label)
		layout.addLayout(tr_layout)
		layout.addWidget(self.button)
				
		self.setLayout(layout)
	
		###################################
		# CONNECTIONS
		###################################
		self.button.clicked.connect(self.notificationDone)
		logging.info('Notification constructor has been finished')
	
	########################
	# SIGNALS
	########################
	showed = QtCore.pyqtSignal()
	
	@Except
	@QtCore.pyqtSlot()
	def notificationDone (self, second_argument):
		logging.info('Has been started function notificationDonde()')
		if (self.tr_field.text().lower() in self.translate):
		#~ if (QtCore.QString(self.translate).toLower() == self.tr_field.text().toLower()):
			if self.attempt == 0:
				self.db_conn.updateWordHeight(self.word_id, self.word_height + 3)
				logging.info('Has been updated a word weight. Attepmpt == 0')
			else:
				self.db_conn.updateWordHeight(self.word_id, self.word_height + 2)
				logging.info('Has been updated a word weight. Attepmpt == {}'.format(self.attempt))
			self.showed.emit()
		else:
			self.attempt+=1
			
	@Except
	def center(self):
		'''move a widget to the center of desctop window'''
		logging.info('Has been start function center()')
		screen = QtGui.QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


class Notifications_container (QtCore.QObject):
	
	@Except
	def __init__ (self, db, parent = None):
		logging.info('Has been started notification_container constructor')
		QtCore.QObject.__init__ (self, parent)
		
		self.dictionary = {}
		self.db = db
		
		logging.info('Has been finished notification constructor')

	#################################
	# SIGNALS
	#################################
	done = QtCore.pyqtSignal(int)
	
	#################################
	# SLOTS
	#################################
	@Except
	@QtCore.pyqtSlot(int, int, str)
	def addNewNotification (self, index, timer, text):
		logging.info('Has been started notification_container.addNewNotification(index = {}, timer = {}, text = {})'.format(index, timer, text))
		self.dictionary[index] = Notification(self.db, index, timer, text)
		self.dictionary[index].timer.start()
		self.dictionary[index].showed.connect(lambda : self.deleteNotification(index))
	
	@Except
	@QtCore.pyqtSlot(int)
	def deleteNotification (self, index):
		logging.info('Has been started notification_container.deleteNotification(index = {})'.format(index))
		if (self.dictionary[index]):
			self.dictionary[index].timer.stop()
			self.dictionary[index].deleteLater()
			self.dictionary[index] = None
			self.done.emit(index)

