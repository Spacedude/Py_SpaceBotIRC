# coding: utf-8

import urllib
from irc.client import NickMask

def on_module_loaded( self ):
	return [ "isup" ]

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
		
		if cmd == "isup":
			if self.hasPermission( e.source.nick, str( e.target ), 15 ):
				if arg != "":
					url = "http://isup.me/%s" % arg
					
					try:
						data = urllib.urlopen( url ).read().decode( "utf-8" )
						
						if "It's just you." in data:
							self.privmsg( target, "It's just you. %s is up" % arg )
						
						elif "It's not just you!" in data:
							self.privmsg( target, "It's not just you! %s looks down from here" % arg )
						
						elif "doesn't look like a site on the interwho." in data:
							self.privmsg( target, "%s doesn't look like a site on the interwho" % arg )
					
					except:
						pass
			
			return True
