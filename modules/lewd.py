# coding: utf-8

import os
import json
from irc.client import NickMask

def on_module_loaded( self ):
	if not "lewd" in self.data:
		self.data[ "lewd" ] = {}
	
	return {
		"lewd": {
			"description": "Give people 'lewd' points or display yours.",
			"syntax": ".lewd[ <nick>]"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".lewd":
		arg = " ".join( argSplit[ 1: ] )

		if self.hasPermission( e.source.nick, e.target, 10 ):
			if argSplit[ 1 ] == e.source.nick or arg == "":
				if argSplit[ 1 ] in self.data[ "lewd" ]:
					self.privmsg( target, "Lewdness for %s: %s" % ( argSplit[ 1 ], self.data[ "lewd" ][ argSplit[ 1 ] ] ) )
				else:
					self.privmsg( target, argSplit[ 1 ] + " is 100% pure." )
			
			else:
				if argSplit[ 1 ] in self.data[ "lewd" ]:
					c_lewd = self.data[ "lewd" ][ argSplit[ 1 ] ] + 1
				else:
					c_lewd = 1
				
				self.data[ "lewd" ][ argSplit[ 1 ] ] = c_lewd
				
				self.saveData()
				
				self.privmsg( target, "Lewdness for %s: %s" % ( argSplit[ 1 ], c_lewd ) )
		
		return True

