#!/usr/bin/env python
import sys
import os
import time
import logging

class Debug():
	def __init__ (self):
		LOG_DIR = os.path.join('/tmp/remy_logs/')
		self.LOG_FILE = os.path.join(LOG_DIR, '{}.log'.format(time.strftime("%Y-%b-%d-%H-%M-%S", time.gmtime())))   
		
		if not os.path.exists(LOG_DIR):
			os.mkdir(LOG_DIR) 

		logging.basicConfig(format = '%(levelname)-2s [%(asctime)s] %(message)s', level = logging.INFO, filename = self.LOG_FILE)
	
	def __del__ (self):
		if os.stat(self.LOG_FILE).st_size == 0:
			os.remove(self.LOG_FILE)
	
def Except (decorated):
	'''Exception decorator'''
	def wrapper (*args, **kwargs):
		try:
			return decorated(*args, **kwargs)
		except Exception as err:
			#~ logging.error(err.args)
			logging.error('__{}__: {}'.format(decorated.__name__, err))
			os.system("zenity --error --text='{}'".format(err))
			raise
	return wrapper
