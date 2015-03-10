# coding: utf-8

from irc.client import NickMask

def on_module_loaded( self ):
	return [] # We don't want this listed in the available commands

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".raw":
		arg = " ".join( argSplit[ 1: ] )
		
		if e.source.nick == "Spacecode":
			if self.hasPermission( e.source.nick, target, 100 ):
				if arg != "":
					self.connection.send_raw( arg )
			
		return True
