# coding: utf-8

import json
import os
import copy
from irc.client import NickMask

def on_module_loaded( self ):
	if not hasattr( self, "permissions" ):
		if os.path.isfile( "permissions.json" ):
			permissionFile = open( "permissions.json", 'r' )
			self.permissions = json.load( permissionFile )
			permissionFile.close()
		
		else:
			print( "No permission file detected. Owner nickname needed." )
			botOwner = raw_input( "Please enter your IRC nickname: " )
			
			self.permissions = {}
			self.permissions[ "__OWNER__" ] = botOwner
			
			permissionFile = open( "permissions.json", 'w' )
			permissionFile.write( json.dumps( self.permissions ) )
			permissionFile.close()
	
	return [ "permission" ]

def on_pubmsg( self, c, e ):
	arg = e.arguments[ 0 ]
	
	if arg[ 0 ] == '.':
		cmdSplit = arg[ 1: ].split()
		cmd = cmdSplit[ 0 ]
		args = cmdSplit[ 1: ]
		
		if cmd == "permission":
			if args[ 0 ].lower() == "set":
				if len( args ) >= 2:
					if self.hasPermission( e.source.nick, e.target, 100 ):
						if not e.target in self.permissions:
							self.permissions[ e.target ] = {}
						
						self.permissions[ e.target ][ args[ 1 ] ] = int( args[ 2 ] )

						permissionFile = open( "permissions.json", 'w' )
						permissionFile.write( json.dumps( self.permissions ) )
						permissionFile.close()

						self.notice( e.source.nick, "Set permission for %s to %s" % ( args[ 1 ], args[ 2 ] ) )

			elif args[ 0 ].lower() == "get":
				if len( args ) >= 1:
					try:
						self.notice( e.source.nick, "Permission for %s: %s" % ( e.source.nick, self.permissions[ e.target ][ e.source.nick ] ) )
					
					except Exception as Ex:
						print Ex
			
			else:
				pass
			
			return True
