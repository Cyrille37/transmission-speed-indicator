#!/usr/bin/env python
"""
	A Gnome/Unity applet indicator to swith transmission-daemon's alt_speed
	Copyright (c) 2013 Cyrille Giquello <cyrille37@gmail.com>
	Licensed under the GPLv3 license.
"""

from __future__ import print_function

import sys
import gtk
import appindicator

# Transmission RPC
# http://pythonhosted.org/transmissionrpc/
# https://bitbucket.org/blueluna/transmissionrpc/wiki/Home
# $ sudo apt-get install python-transmissionrpc
import transmissionrpc

# http://pymotw.com/2/ConfigParser/
from ConfigParser import SafeConfigParser

import logging

class EssaiIndicator01:

	PROGRAM_NAME = 'transmission-speed-indicator'
	CONFIG_FILENAME = 'transmission-speed-indicator.ini'
	CONFIG_SECTION = 'TRANSMISSION-SPEED-INDICATOR'
	ICON_NOSERVER = 'transmission-speed-noserver-tray-icon.svg'
	ICON_HIGH = 'transmission-speed-high-tray-icon.svg'
	ICON_LOW = 'transmission-speed-low-tray-icon.svg'

	def __init__(self):

		self.base_folder = sys.path[0]
		self.icons_folder = self.base_folder
		self.trpc = None
		self.alt_speed_enabled = False ;

		self.ind = appindicator.Indicator("debian-doc-menu",
																		 self.icons_folder + '/' + self.ICON_NOSERVER,
																		 appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)
		self.menu_setup()
		self.ind.set_menu(self.menu)

	def check_alt_speed_enabled(self):

		# Bad code:
		# I do not know how to check a CheckMenuItem without throwing the signal.
		# So I use a variable to avoid an infinite loop ...
		self.check_running = True

		if self.getTRpc() == None:
			self.alt_speed_enabled_item.set_inconsistent(True)
			self.ind.set_icon(self.icons_folder + '/' + self.ICON_NOSERVER )
			return True

		try :
			sess = self.trpc.get_session()
			#print( "alt speed :", sess.alt_speed_enabled)
		except :
			self.trpc = None
			return True ;

		if sess.alt_speed_enabled :
			self.ind.set_icon(self.icons_folder + '/' + self.ICON_LOW )
			if self.alt_speed_enabled_item.get_active() != True :
				self.alt_speed_enabled_item.set_active(True)
		else :
			self.ind.set_icon(self.icons_folder + '/' + self.ICON_HIGH )
			if self.alt_speed_enabled_item.get_active():
				self.alt_speed_enabled_item.set_active(False)

		self.alt_speed_enabled = sess.alt_speed_enabled

		self.check_running = False

		return True

	def menu_alt_speed_enabled(self, widget):

		if self.check_running or self.trpc == None :
			return

		self.check_alt_speed_enabled()
		if self.alt_speed_enabled :
			self.trpc.set_session(alt_speed_enabled=False)
		else :
			self.trpc.set_session(alt_speed_enabled=True)
		self.check_alt_speed_enabled()

	def getTRpc(self):

		if self.trpc == None :
			#print( "looking for a server ... "+ self.server)
			try:
				self.trpc = transmissionrpc.Client(address=self.server,port=self.port, user=self.user, password=self.password, timeout=self.timeout);
			except transmissionrpc.error.TransmissionError as e :
				# do not throw error if server is unreachable
				# 111 refused connection
				# 401 basic auth failed
				if e.original.code != 600 and e.original.code != 101 :
					#print(e)
					self.displayErrorAndExit( "Could not access remote transmission server.\nCheck the configuration file '{0}'.\n\n\tError is: {1}\n\nRaw error: {2}".format(self.CONFIG_FILENAME, e.original.message, e.original) )

		return self.trpc

	def displayErrorAndExit(self, error):

		label = gtk.Label( error)
		label.set_selectable(True)
		d = gtk.Dialog( self.PROGRAM_NAME, None, gtk.DIALOG_MODAL , (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT) )
		d.set_border_width(18)
		d.set_position(gtk.WIN_POS_CENTER)
		d.vbox.pack_start(label)
		d.show_all();
		d.run()
		sys.exit(0);

	def menu_setup(self):
		self.menu = gtk.Menu()

		self.alt_speed_enabled_item = gtk.CheckMenuItem("Alt speed")
		self.alt_speed_enabled_item.connect("activate", self.menu_alt_speed_enabled)
		#self.alt_speed_enabled_item.connect("toggled", self.menu_alt_speed_enabled)
		self.alt_speed_enabled_item.show()
		self.menu.append(self.alt_speed_enabled_item)

		self.quit_item = gtk.MenuItem("Quit")
		self.quit_item.connect("activate", self.quit)
		self.quit_item.show()
		self.menu.append(self.quit_item)

	def quit(self, widget):
		sys.exit(0)

	def main(self):

		parser = SafeConfigParser()
		
		try:
			parser.read(self.base_folder + '/' + self.CONFIG_FILENAME)
			self.server = parser.get(self.CONFIG_SECTION, 'server')
			self.port = parser.getint(self.CONFIG_SECTION, 'port')
			self.user = parser.get(self.CONFIG_SECTION, 'user')
			self.password = parser.get(self.CONFIG_SECTION, 'password')
			self.timeout = parser.getint(self.CONFIG_SECTION, 'timeout')
			rpc_interval = parser.getint(self.CONFIG_SECTION, 'rpc_interval')
			
		except Exception as e :
			print( e );
			self.displayErrorAndExit( "Could not read configuration '"+self.CONFIG_FILENAME+"'\nError is: "+e.message)

		if parser.has_option(self.CONFIG_SECTION, "rpc_logger_level"):
			transmissionrpc.utils.add_stdout_logger(parser.get(self.CONFIG_SECTION, 'rpc_logger_level'));

		self.check_alt_speed_enabled()

		# The callback function is called repeatedly until it returns False,
		# at which point the timeout is automatically destroyed and the function will not be called again
		# http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gobject--timeout-add
		gtk.timeout_add( rpc_interval * 1000, self.check_alt_speed_enabled)

		gtk.main()

if __name__ == "__main__":
    indicator = EssaiIndicator01()
    indicator.main()
