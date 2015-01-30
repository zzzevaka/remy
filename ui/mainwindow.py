#! /usr/bin/env python

import sys
import os
from debug import Except
import logging
from PyQt4 import QtCore, QtGui
from debug import Except


class Help (QtGui.QLabel):
	@Except
	def __init__ (self, parent = None):
		QtGui.QLabel.__init__ (self, parent)
		self.resize(450,100)
		text = '''Remy - reminder which can help you learn foreign words.
		Version  - 0.1
		Autor - L.Maksimov zzzevaka@gmail.com'''
		self.setText(text)
		#~ self.setAlignment(QtCore.Qt.AlignCenter);

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
		#~ logging.info('Has been started SystemTrayIcon constructor')s
        QtGui.QSystemTrayIcon.__init__(self, parent)

        self.setIcon(QtGui.QIcon(os.path.expanduser("~/Dropbox/Reminder/icons/64.png")))

        self.iconMenu = QtGui.QMenu(parent)
        self.main_window = self.iconMenu.addAction("&Main Window")
        self.new_button = self.iconMenu.addAction("&New notification")
        self.exit_button = self.iconMenu.addAction("&Exit")
        self.setContextMenu(self.iconMenu)
        self.show()
	
    def appExit(self):
        sys.exit()

class MainWindowWidget (QtGui.QMainWindow):
	@Except
	def __init__ (self, db, parent=None):
		QtGui.QMainWindow.__init__ (self, parent)
		
		self.center()
		self.resize(800,350)
		self.setWindowTitle('remy')
		self.setWindowIcon(QtGui.QIcon(os.path.expanduser("~/Dropbox/Reminder/icons/test.png")))
		self.statusBar().showMessage('Ready')
		
		self.tray = SystemTrayIcon()
		###########################################
		# MAIN MENU
		###########################################
		# new notification button
		new_action =  QtGui.QAction(QtGui.QIcon('icons/new.png'), '&New notification', self)
		new_action.setShortcut('Ctrl+N')
		new_action.setStatusTip('Create new notification')
		# help button
		self.h = Help()
		help_action = QtGui.QAction(QtGui.QIcon('icons/new.png'), '&Help', self)
		help_action.setShortcut('Ctrl+H')
		help_action.setStatusTip('Show help')
		# exit button
		exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
		exit_action.setShortcut('Ctrl+Q')
		exit_action.setStatusTip('Exit application')
		# create a menubar
		menubar = self.menuBar()
		file = menubar.addMenu('&File')
		file.addAction(new_action)
		file.addAction(help_action)
		file.addAction(exit_action)
		
		###########################################
		# DATABASE CONNECTION
		###########################################
		self.db_connection = db		
		###########################################
		# TABLE WITH CURRENT NOTTIFICATIONS
		###########################################
		# create a table
		self.table = QtGui.QTableWidget(0, 2)
		self.table.setHorizontalHeaderLabels(['Time', 'Notification text'])
		header = self.table.horizontalHeader()
		header.setStretchLastSection(True)
		# set width of  date column
		self.table.setColumnWidth(0,160)
		# set cells no editible
		self.table.setEditTriggers( QtGui.QTableWidget.NoEditTriggers )
		# add rows
		self.paintTable()
		
		###########################################
		# PUSH BUTTONS
		###########################################
		self.delete_button = QtGui.QPushButton('Delete notification', self)
		self.delete_button.setStatusTip('Delete a notification')
		new_button = QtGui.QPushButton('New notification', self)
		new_button.setStatusTip('Add a new notification')	
		
		###########################################
		# LAYOTS
		###########################################
		mainWidget = QtGui.QWidget()
		# Button horizaontal layout
		mainWidget.buttonLayout = QtGui.QHBoxLayout()
		mainWidget.buttonLayout.addWidget(new_button)
		mainWidget.buttonLayout.addWidget(self.delete_button)
		# Main Layout
		mainWidget.mainlayout = QtGui.QVBoxLayout()
		mainWidget.mainlayout.addWidget(self.table)
		mainWidget.mainlayout.addLayout(mainWidget.buttonLayout)
		mainWidget.setLayout(mainWidget.mainlayout)
		# set a central widget of mainwindow
		self.setCentralWidget(mainWidget)
		
		###########################################
		# CONNECTIONS
		###########################################
		self.connect(exit_action, QtCore.SIGNAL('triggered()'), QtGui.qApp.quit)
		new_action.triggered.connect(lambda : self.newButtonClicked.emit())
		new_button.clicked.connect(lambda : self.newButtonClicked.emit())
		help_action.triggered.connect(self.h.show)
		self.delete_button.clicked.connect(self.deleteRow)
	
	###################################
	# SIGNALS
	###################################
	newButtonClicked = QtCore.pyqtSignal()
	deleteNotification = QtCore.pyqtSignal(str, str)
	
	###################################
	# SLOTS
	###################################
	@Except
	@QtCore.pyqtSlot()
	def paintTable(self):
		self.table.clearContents()
		# get rows count
		rows = self.db_connection.query("SELECT count(*) FROM notification WHERE status == 0").fetchone()[0]
		self.table.setRowCount(rows)
		# get notification from data base
		for c, row in zip(range(0, rows), self.db_connection.getAllCurrentNotifications()):
			tmp_date = QtGui.QTableWidgetItem(row[2])
			tmp_text = QtGui.QTableWidgetItem(row[1])
			self.table.setItem(c, 0, tmp_date)
			self.table.setItem(c, 1, tmp_text)
		# set current cells to nothing
		self.table.setCurrentCell(-1,-1)

	@Except	
	@QtCore.pyqtSlot(str, str)
	def addRow(self, text, dateTime):
		row = self.table.rowCount()
		self.table.insertRow(row)
		tmp_text = QtGui.QTableWidgetItem(text)
		tmp_date = QtGui.QTableWidgetItem(dateTime)
		self.table.setItem(row, 0, tmp_text)
		self.table.setItem(row, 1, tmp_date)		

	@Except	
	@QtCore.pyqtSlot()
	def deleteRow(self, l):
		row = self.table.currentRow()
		'''delete row from table and data base'''
		if (row != -1):
			#delete from data base
			tmp_date = self.table.takeItem(row,0).text()
			tmp_text = self.table.takeItem(row,1).text()
			self.deleteNotification.emit(tmp_date, tmp_text)
		else:
			self.statusBar().showMessage('At first select a row to delete')
	
	###########################################
	# METHODS
	###########################################
	@Except
	def center(self):
		'''move widget to the center of desctop window'''
		screen = QtGui.QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


