# coding: utf-8

import sys
import traceback
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
	def __init__( self, data ):
		self.data = data
		self.modules = {}
		self.modulenames = []
		self.modulecommands = []
		self.reloadModules()
		self._rfc_1459_command_regexp = re.compile( r"^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?" )
		
		irc.bot.SingleServerIRCBot.__init__(
			self,
			[
				irc.bot.ServerSpec(
					self.data[ "settings" ][ "server" ],
					int( self.data[ "settings" ][ "port" ] ),
					self.data[ "settings" ][ "password" ]
				)
			],
			self.data[ "settings" ][ "nickname" ],
			"SpaceBot",
			10
		)
		
		self.connection.username = self.data[ "settings" ][ "username" ]
	
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
		
		if "permission" in self.data:
			if "__OWNER__" in self.data[ "permissions" ]:
				if user == self.data[ "permissions" ][ "__OWNER__" ]:
					return True

			if target in self.data[ "permissions" ]:
				if user in self.data[ "permissions" ][ target ]:
					if self.data[ "permissions" ][ target ][ user ] >= level:
						return True
		
		self.notice( user, "Check your privilege :^)" )
		
		return False
	
	def saveData( self ):
		datafile = open( "data.json",'w' )
		datafile.write( json.dumps( self.data, sort_keys = True, indent = 4, separators = ( ",", ": " ) ) )
		datafile.close()

	def on_welcome( self, c, e ):
		if "nickpass" in self.data[ "settings" ]:
			if self.data[ "settings" ][ "nickpass" ] != None and self.data[ "settings" ][ "nickpass" ] != "":
				c.privmsg( "NickServ", "identify " + self.data[ "settings" ][ "nickpass" ] )
	
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
			print( traceback.format_exc() )
			c.privmsg( "Spacecode", Ex )
	
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
					print( "Loading module '%s' ..." % module )
					
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

if os.path.isfile( "data.json" ):
	print( "Data file detected" )
	
	datafile = open( "data.json",'r' )
	data = json.load( datafile )
	datafile.close()

else:
	print( "No data file detected." )
	
	data = {}
	data[ "settings" ] = {}

	data[ "settings" ][ "server" ] = raw_input( "Please enter the server to connect to: " )
	data[ "settings" ][ "port" ] = raw_input( "Please enter the server port (leave blank for default): " )
	data[ "settings" ][ "username" ] = raw_input( "Please enter the user name: ")
	data[ "settings" ][ "password" ] = raw_input( "Please enter the server password (leave blank if none): " )
	data[ "settings" ][ "nickname" ] = raw_input( "Enter the bots nick: ")
	data[ "settings" ][ "nickpass" ] = raw_input( "Please enter the nickserv password (leave blank if none): " )
	
	if data[ "settings" ][ "port" ] == "":
		data[ "settings" ][ "port" ] = "6667"
	
	datafile = open( "data.json",'w' )
	datafile.write( json.dumps( data, sort_keys = True, indent = 4, separators = ( ",", ": " ) ) )
	datafile.close()

while True:
	try:
		bot = SpaceBot( data )
		bot.start()
	
	except KeyboardInterrupt:
		break
	
	except:
		try:
			print( traceback.format_exc() )

		except:
			print( "\nwhat the FUGG\n" )

