# coding: utf-8

import os
import json
from irc.client import NickMask

def on_module_loaded( self ):
	if not hasattr( self, "lewdDict" ):
		if os.path.isfile( "lewd.json" ):
			lewdFile = open( "lewd.json", 'r' )
			self.lewdDict = json.load( lewdFile )
			lewdFile.close()
		
		else:
			self.lewdDict = {}
	
	return [ "lewd" ]

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick, e.arguments[ 0 ] )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target, e.arguments[ 0 ] )

def on_dccmsg( self, c, e ):
	do_command( self, e, e.source, e.arguments[ 0 ] )
	
def do_command( self, e, target, arg ):
	if arg[ 0 ] == '.':
		cmdSplit = arg[ 1: ].split()
		cmd = cmdSplit[ 0 ]
		args = cmdSplit[ 1: ]
		arg = " ".join( args )
		
		if cmd == "lewd":
			if self.hasPermission( e.source.nick, e.target, 10 ):
				if arg != "":
					if args[ 0 ] == e.source.nick:
						if args[ 0 ] in self.lewdDict:
							self.privmsg( target, "Lewdness for %s: %s" % ( args[ 0 ], self.lewdDict[ args[ 0 ] ] ) )
						else:
							self.privmsg( target, "%s wasn't lewd yet." % ( args[ 0 ] ) )
					
					else:
						if args[ 0 ] in self.lewdDict:
							c_lewd = self.lewdDict[ args[ 0 ] ]
						else:
							c_lewd = 0

						self.lewdDict[ args[ 0 ] ] = c_lewd + 1
						
						lewdFile = open( "lewd.json", 'w' )
						lewdFile.write( json.dumps( self.lewdDict ) )
						lewdFile.close()
						
						self.privmsg( target, "Lewdness for %s: %s" % ( args[ 0 ], self.lewdDict[ args[ 0 ] ] ) )
				
				else:
					if e.source.nick in self.lewdDict:
						self.privmsg( target, "Lewdness for %s: %s" % ( e.source.nick, self.lewdDict[ e.source.nick ] ) )
					
					else:
						self.privmsg( target, "%s wasn't lewd yet." % ( e.source.nick ) )
			
			return True
