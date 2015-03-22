# coding: utf-8

from irc.client import NickMask
import random

def on_module_loaded( self ):
	return {
		"decide": {
			"description": "Gives a random decision from the given choices.",
			"syntax": ".decide <choice> or <choice> [or <choice>\x09etc.\x0f]"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".decide":
		arg = " ".join( argSplit[ 1: ] )
		
		if self.hasPermission( e.source.nick, target, 10 ):
			choices = []
			argLeft = arg + ""
			
			while argLeft.find( " or " ) != -1:
				choices.append( argLeft[ :argLeft.find( " or " ) ] )
				argLeft = argLeft[ argLeft.find( " or " ) + 4: ]
			
			choices.append( argLeft )
			
			self.privmsg( target, e.source.nick + ": " + random.choice( choices ) )

		return True

