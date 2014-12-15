# coding: utf-8

from irc.client import NickMask

def on_module_loaded( self ):
	return [] #We don't want this listed in the available commands

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
		
		if cmd == "raw":
			if self.hasPermission( e.source.nick, str( e.target ), 100 ):
				if arg != "":
					self.connection.send_raw( arg )
				
			return True
