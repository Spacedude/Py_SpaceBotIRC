# coding: utf-8

import sys
import os
import re
import json
import imp
import irc.bot
import irc.strings
import datetime
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from inspect import getmembers, isfunction

class SpaceBot( irc.bot.SingleServerIRCBot ):
	def __init__( self, settings ):
		self.settings = settings
		self.modules = {}
		self.modulenames = []
		self.modulecommands = []
		self.lastFMApiKey = settings[ "lastfmapikey" ]
		self.reloadModules()
		self._rfc_1459_command_regexp = re.compile( r"^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?" )
		
		irc.bot.SingleServerIRCBot.__init__(
			self,
			[
				irc.bot.ServerSpec(
					settings[ "server" ],
					int( settings[ "port" ] ),
					settings[ "password" ]
				)
			],
			settings[ "nickname" ],
			"SpaceBot",
			10
		)
		
		self.connection.username = settings[ "username" ]
	
	def privmsg( self, target, message ):
		timestamp = datetime.datetime.utcnow()
		timestamp = timestamp + datetime.timedelta( hours = 1 )
		print "%s - [%s] <%s> %s" % ( timestamp.strftime( "%H:%M:%S" ), target, self.connection.get_nickname(), message )
		self.connection.privmsg( target, message )
	
	def notice( self, target, message ):
		timestamp = datetime.datetime.utcnow()
		timestamp = timestamp + datetime.timedelta( hours = 1 )
		print "%s - [%s] -%s- %s" % ( timestamp.strftime( "%H:%M:%S" ), target, self.connection.get_nickname(), message )
		self.connection.notice( target, message )

	def hasPermission( self, user, target, level ):
		return True
		
		if hasattr( self, "permissions" ):
			if "__OWNER__" in self.permissions:
				if user == self.permissions[ "__OWNER__" ]:
					return True

			if target in self.permissions:
				if user in self.permissions[ target ]:
					if self.permissions[ target ][ user ] >= level:
						return True
		
		self.notice( user, "Check your privilege :^)" )
		
		return False
	
	def on_welcome( self, c, e ):
		if "nickpass" in self.settings:
			if self.settings[ "nickpass" ] != None and self.settings[ "nickpass" ] != "":
				c.privmsg( "NickServ", "identify " + self.settings[ "nickpass" ] )
	
	def on_ctcp( self, c, e ):
		nick = e.source.nick
		
		if e.arguments[ 0 ] == "VERSION":
			c.ctcp_reply( nick, "Stop the version requests you filthy human" )
		
		elif e.arguments[ 0 ] == "PING":
			if len( e.arguments ) > 1:
				c.ctcp_reply( nick, "PING " + e.arguments[ 1 ] )
	
	def on_all_raw_messages( self, c, e ):
		self.processCommand( "on_all_raw_messages", c, e )
	
	def on_nicknameinuse( self, c, e ):
		c.nick( c.get_nickname() + "_" )
	
	def on_privmsg( self, c, e ):
		timestamp = datetime.datetime.utcnow()
		timestamp = timestamp + datetime.timedelta( hours = 1 )
		print( "%s - [%s] <%s> %s" % ( timestamp.strftime( "%H:%M:%S" ), e.source.nick, e.source.nick, e.arguments[ 0 ] ) )
		self.processCommand( "on_privmsg", c, e )
	
	def on_pubmsg( self, c, e ):
		timestamp = datetime.datetime.utcnow()
		timestamp = timestamp + datetime.timedelta( hours = 1 )
		print( "%s - [%s] <%s> %s" % ( timestamp.strftime( "%H:%M:%S" ), e.target, e.source.nick, e.arguments[ 0 ] ) )
		self.processCommand( "on_pubmsg", c, e )
	
	def processCommand( self, func, c, e ):
		try:
			if self.modules:
				for module in self.modulenames:
					if hasattr( self.modules[ module ], func ):
						shouldBreak = getattr( self.modules[ module ], func )( self, c, e )
						
						if shouldBreak == True:
							break
		except Exception as Ex:
			pass
	
	def reloadModules( self, printTarget = None ):
		oldModnames = self.modulenames
		oldMods = self.modules
		self.modulenames = []
		self.modules = {}
		newMods = 0
		reloadedMods = 0
		
		for item in os.listdir( "modules" ):
			moduleSplit = item.split( '.' )
			module = moduleSplit[ 0 ]
			moduleExt = moduleSplit[ len( moduleSplit ) - 1 ]
			
			if module != "__init__":
				if moduleExt == "py":
					print "Loading module " + module
					
					if any( module in s for s in oldModnames ):
						self.modules[ module ] = reload( oldMods[ module ] )
						reloadedMods += 1
					
					else:
						exec( "import modules.%s" % module ) in globals(), locals()
						self.modules[ module ] = eval( "modules.%s" % module )
						newMods += 1
					
					if hasattr( self.modules[ module ], "on_module_loaded" ):
						c_modulecommands = getattr( self.modules[ module ], "on_module_loaded" )( self )
						self.modulecommands = list( set( c_modulecommands + self.modulecommands ) )
					
					self.modulenames.append( module )
		
		if printTarget != None:
			self.notice( printTarget, "Reloaded %s modules and found %s new ones." % ( reloadedMods, newMods ) )

if os.path.isfile( "startsettings.json" ):
	print( "Config file detected" )
	
	settingsFile = open( "startsettings.json",'r' )
	settings = json.load( settingsFile )
	settingsFile.close()

else:
	settings = {}
	
	print "No config file detected."
	
	settings[ "server" ] = raw_input( "Please enter the server to connect to: " )
	settings[ "port" ] = raw_input( "Please enter the server port (leave blank for default): " )
	settings[ "username" ] = raw_input( "Please enter the user name: ")
	settings[ "password" ] = raw_input( "Please enter the server password (leave blank if none): " )
	settings[ "nickname" ] = raw_input( "Enter the bots nick: ")
	settings[ "nickpass" ] = raw_input( "Please enter the nickserv password (leave blank if none): " )
	settings[ "lastfmapikey" ] = raw_input( "Please enter your last.fm api key: " )
	
	if settings[ "port" ] == "":
		settings[ "port" ] = "6667"
	
	configfile = open( "startsettings.json",'w' )
	configfile.write( json.dumps( settings ) )
	configfile.close()

while True:
	try:
		bot = SpaceBot( settings )
		bot.start()
	except KeyboardInterrupt:
		break
	except:
		try:
			print traceback.format_exc()
		except:
			print "\nwhat the FUGG\n"
