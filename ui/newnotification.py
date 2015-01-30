#!/usr/bin/env python

import sys
import logging
from PyQt4 import QtGui, QtCore
from debug import Except

class NewNotificationWidget (QtGui.QWidget):
	
	@Except
	def __init__ (self, parent = None):
		
		QtGui.QWidget.__init__ (self, parent)
		##########################################
		# SET WIDGET OPTIONS
		##########################################
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.resize(500,70)
		self.center()
		self.setWindowTitle('remy new notification')
				
		##########################################
		# VARIABLES
		##########################################
		self.dateTime = QtCore.QDateTime( QtCore.QDate.currentDate(), QtCore.QTime.currentTime())
		self.text = ''
		self.text_edit = QtGui.QTextEdit()
		self.add_button = QtGui.QPushButton('Remind me', self)
		self.statusBar = QtGui.QStatusBar()
		
		##########################################
		# DATE AND TIME
		##########################################
		#date
		self.date_edit = QtGui.QDateEdit(QtCore.QDate.currentDate())
		self.date_edit.setDisplayFormat("dd.MM.yyyy");
		self.date_label = QtGui.QLabel("Date:")
		#time
		self.time_edit = QtGui.QTimeEdit(QtCore.QTime.currentTime())
		self.time_edit.setDisplayFormat("hh.mm.ss");
		self.time_label = QtGui.QLabel("Time:")
		#date and time layout
		dateTimeLayout = QtGui.QHBoxLayout()
		dateTimeLayout.setSpacing(5)
		dateTimeLayout.addWidget(self.date_label)
		dateTimeLayout.addWidget(self.date_edit)
		dateTimeLayout.addWidget(self.time_label)
		dateTimeLayout.addWidget(self.time_edit)
			
		##########################################
		# UPPER LAYOUT
		##########################################
		#includes dateTimeLayout and button
		upperLayout = QtGui.QHBoxLayout()
		upperLayout.setSpacing(70)
		upperLayout.addLayout(dateTimeLayout)
		upperLayout.addWidget(self.add_button)
			
		##########################################
		# MAIN LAYOUT
		##########################################
		mainlayout = QtGui.QVBoxLayout()
		mainlayout.addLayout(upperLayout)
		mainlayout.addWidget(self.text_edit)
		mainlayout.addWidget(self.statusBar)
		self.setLayout(mainlayout)
			
		###########################################
		# CONNECTIONS
		###########################################
		self.connect(self.add_button, QtCore.SIGNAL('clicked()'), self.commitNotification)
		self.connect(self.date_edit, QtCore.SIGNAL('dateChanged(QDate)'), self.dateTime.setDate)
		self.connect(self.time_edit, QtCore.SIGNAL('timeChanged(QTime)'), self.dateTime.setTime)
		self.connect(self.text_edit, QtCore.SIGNAL('textChanged()'), self.changeText)
	
	@QtCore.pyqtSlot()
	def showWidget(self):
		'''clear widget ans show'''
		self.text = ''
		self.dateTime.setDate(QtCore.QDate.currentDate())
		self.dateTime.setTime(QtCore.QTime.currentTime())
		self.text_edit.clear()
		self.date_edit.setDate(QtCore.QDate.currentDate())
		self.time_edit.setTime(QtCore.QTime.currentTime())
		self.show()

	###############################
	# SIGNALS
	###############################
	addNewNotificaion = QtCore.pyqtSignal(str, str)
	addNewNotification2 = QtCore.pyqtSignal()
	
	@Except		
	def changeText (self):
		'''change text of notification'''
		self.text = self.text_edit.toPlainText()
	@Except	
	def center(self):
		'''move widget to the center of desctop window'''
		screen = QtGui.QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

	@Except		
	def commitNotification (self):
		'''adding notification to DB. Check date< time and text'''
		if (not self.text):
			self.statusBar.showMessage('Notification without text - strange!')
		elif (self.dateTime <= QtCore.QDateTime.currentDateTime()):
			self.statusBar.showMessage("If i had a time machine, i would do it")
		else:
			self.statusBar.showMessage("Adding notification to database")
			self.addNewNotificaion.emit(self.dateTime.toString("yyyy-MM-dd hh:mm:ss"), self.text)
			self.addNewNotification2.emit()
			#~ self.clearWidget()
			self.close()				

