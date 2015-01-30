#!/usr/bin/env python

# import embedded libs
import os
import sys
import logging
import shutil
# check python version
if (float(sys.version[:3]) < 3):
	os.system("zenity --error --text='minimal python version = 3'")
	sys.exit(1)

# import 
try:
	# external depends
	from PyQt4 import QtGui, QtCore
	# internal depends
	sys.path.insert(0, os.path.expanduser('~/Dropbox/Reminder/ui'))
	import debug
	from notification import Notification, Notifications_container
	from mainwindow import MainWindowWidget
	from newnotification import NewNotificationWidget
	#~ from trayicon import SystemTrayIcon
	from db import DBconnect
	from dictionary import DictionaryUpdater
except ImportError as err:
	os.system("zenity --error --text='Python ImportError: {}'".format(err))
	sys.exit(1)


@debug.Except
def main():
	#debug init
	d = debug.Debug()
	logging.info('Remy has been started')
	
	# QT Application
	qapp = QtGui.QApplication(sys.argv)
	qapp.setQuitOnLastWindowClosed(False)
	# check dir exists. If it doesn't exist - make
	path = os.path.expanduser('~/.reminder/')
	if not os.path.exists(os.path.expanduser(path)):
		os.makedirs(path)
		#~ debug.log('Dir {} has been made'.format(path))

    # TMP	
	shutil.copy(os.path.expanduser('~/Dropbox/Reminder/dictionaries/people.json'), '{}dictionary.json'.format(path))
	
	# a database connection
	db_connect = DBconnect()
	# create widgets
	new_notification_widget = NewNotificationWidget()
	main_window = MainWindowWidget(db_connect)
	#create a notitifction container	
	notifications = Notifications_container(db_connect)
	# a dictionary updater
	dic_upd = DictionaryUpdater(db_connect)
	# get all actual notifications from DB and create notification objects
	notification_array_tmp = []
	#~ for row in 
		#~ notification_array_tmp.append(row)
	#~ 
	for row in db_connect.getAllCurrentNotifications():
		logging.info('MAIN: Get a notification from db: {}'.format(row))
		secs_to_event = QtCore.QDateTime.currentDateTime().secsTo(QtCore.QDateTime.fromString(row[2], 'yyyy-MM-dd hh:mm:ss'))
		logging.info('MAIN: Add a new notification: id = {} secs_to_event = {} text = {}'.format(row[0], secs_to_event, row[1]))
		notifications.addNewNotification(row[0], secs_to_event, row[1])
		
			
	########################################
	# CONNECTIONS
	########################################
	# tray buttons
	main_window.tray.main_window.triggered.connect(main_window.show)
	main_window.tray.new_button.triggered.connect(new_notification_widget.showWidget)
	main_window.tray.exit_button.triggered.connect(QtGui.qApp.quit)
	# a new notifcation button from mainWidget
	main_window.newButtonClicked.connect(new_notification_widget.showWidget)
	# a table ha been changed
	db_connect.table_changed.connect(main_window.paintTable)
	# add a notification
	new_notification_widget.addNewNotificaion.connect(db_connect.addNotification)
	db_connect.add_notification.connect(notifications.addNewNotification)
	# delete a notification
	main_window.deleteNotification.connect(db_connect.deleteNotificationByVal)
	notifications.done.connect(db_connect.deleteNotificationById)
	db_connect.delete_notification.connect(notifications.deleteNotification)
	# update a dictionary file
	#~ db_connect.table_changed.connect(dic_upd.updateFile)
	
	sys.exit(qapp.exec_())
	
if __name__ == '__main__':
	main()
