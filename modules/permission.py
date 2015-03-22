# coding: utf-8

import json
import os
from irc.client import NickMask

def on_module_loaded( self ):
	if not "permissions" in self.data:
		self.data[ "permission" ] = {}
	
	return {
		"permission": {
			"description": "Sets or gets permissions of a person.",
			"syntax": ".permission <set|get> <power>"
		}
	}

def on_pubmsg( self, c, e ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()
	
	if argSplit[ 0 ] == ".permission":
		arg = " ".join( argSplit[ 1: ] )

		if argSplit[ 1 ].lower() == "set":
			if len( argSplit ) > 3:
				if self.hasPermission( e.source.nick, e.target, 100 ):
					if not e.target in self.data[ "permission" ]:
						self.data[ "permission" ][ e.target ] = {}
					
					self.data[ "permission" ][ e.target ][ argSplit[ 2 ] ] = int( argSplit[ 3 ] )
					self.saveData()
					self.notice( e.source.nick, "Set permission for %s to %s" % ( argSplit[ 2 ], argSplit[ 3 ] ) )
		
		elif argSplit[ 1 ].lower() == "get":
			if len( argSplit ) > 2:
				try:
					self.notice( e.source.nick, "Permission for %s: %s" % ( e.source.nick, self.data[ "permission" ][ e.target ][ e.source.nick ] ) )
				
				except Exception as Ex:
					print( Ex )
		
		else:
			pass
		
		return True

