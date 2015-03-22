# coding: utf-8

import urllib
from irc.client import NickMask

def on_module_loaded( self ):
	return {
		"isup": {
			"description": "Checks if the given website is up or not.",
			"syntax": ".isup <url>"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".isup":
		arg = " ".join( argSplit[ 1: ] )
		
		if self.hasPermission( e.source.nick, target, 15 ):
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
