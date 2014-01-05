#!/usr/bin/env python
#
# Python transmissionrpc :
# http://pythonhosted.org/transmissionrpc/
#

from __future__ import print_function

import sys
import gtk
import appindicator

#import imaplib
import re

# Transmission RPC
# https://bitbucket.org/blueluna/transmissionrpc/wiki/Home
# $ sudo apt-get install python-transmissionrpc
import transmissionrpc

from ConfigParser import SafeConfigParser

import logging

PING_FREQUENCY = 60

class EssaiIndicator01:

	PROGRAM_NAME = "transmission-speed-indicator"

	def __init__(self):
		self.icons_folder = sys.path[0]
		self.ind = appindicator.Indicator("debian-doc-menu",
																		 self.icons_folder + "/transmission-speed-tray-icon.svg",
																		 appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)
		self.menu_setup()
		self.ind.set_menu(self.menu)

	def check_alt_speed_enabled(self):

		# Bad code:
		# I do not know how to check a CheckMenuItem without throwing the signal.
		# So I use a variable to avoid an infinite loop ...
		self.check_running = True

		sess = self.trpc.get_session()
		print( "alt speed :", sess.alt_speed_enabled)
		if sess.alt_speed_enabled :
			self.ind.set_icon(self.icons_folder + "/transmission-speed-low-tray-icon.svg")
			if self.alt_speed_enabled_item.get_active() != True :
				self.alt_speed_enabled_item.set_active(True)
		else :
			self.ind.set_icon(self.icons_folder + "/transmission-speed-high-tray-icon.svg")
			if self.alt_speed_enabled_item.get_active():
				self.alt_speed_enabled_item.set_active(False)

		self.check_running = False

		return sess.alt_speed_enabled

	def alt_speed_enabled(self, widget):

		if self.check_running:
			return

		if self.check_alt_speed_enabled() :
			self.trpc.set_session(alt_speed_enabled=False)
		else :
			self.trpc.set_session(alt_speed_enabled=True)
		self.check_alt_speed_enabled()

	def menu_setup(self):
		self.menu = gtk.Menu()

		self.alt_speed_enabled_item = gtk.CheckMenuItem("Alt speed")
		self.alt_speed_enabled_item.connect("activate", self.alt_speed_enabled)
		#self.alt_speed_enabled_item.connect("toggled", self.alt_speed_enabled)
		self.alt_speed_enabled_item.show()
		self.menu.append(self.alt_speed_enabled_item)

		self.quit_item = gtk.MenuItem("Quit")
		self.quit_item.connect("activate", self.quit)
		self.quit_item.show()
		self.menu.append(self.quit_item)

	def quit(self, widget):
		sys.exit(0)

	def displayErrorAndExit(self, error):
		
		label = gtk.Label(error)
		label.show()
		d = gtk.Dialog( self.PROGRAM_NAME, None, gtk.DIALOG_MODAL , (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT) )
		d.vbox.pack_start(label)
		d.run()
		sys.exit(0);

	def main(self):

		parser = SafeConfigParser()
		parser.read(self.PROGRAM_NAME+'.ini')

		server = parser.get('DEFAULT', 'server')
		port = parser.get('DEFAULT', 'port')
		user = parser.get('DEFAULT', 'user')
		password = parser.get('DEFAULT', 'password')
		print( 'server:', server , port, user, password)

		try:
			self.trpc = transmissionrpc.Client(address=server,port=port, user=user, password=password);
		except transmissionrpc.error.TransmissionError as e :
			print ("ERROR: " + e.original.message,file = sys.stderr)
			self.displayErrorAndExit( "Could not access remote transmission server.\nError is: "+e.original.message)

		logging.getLogger('transmissionrpc').setLevel(logging.INFO)

		self.check_alt_speed_enabled()
		gtk.timeout_add(PING_FREQUENCY * 1000, self.check_alt_speed_enabled)
		gtk.main()

if __name__ == "__main__":
    indicator = EssaiIndicator01()
    indicator.main()
