# coding: utf-8

from irc.client import NickMask

def on_module_loaded( self ):
    return {
		"help": {
			"description": "It's help, DUH!",
			"syntax": ".help [command]"
		}
	}

def on_privmsg( self, c, e ):
    do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
    do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ].lower()
	argSplit = arg.split()

	if argSplit[ 0 ] == ".help":
		if len( argSplit ) > 1:
			if argSplit[ 1 ] in self.help:
				self.privmsg( target, "\x03%s\x0f: %s Syntax: \x03%s" % (
					argSplit[ 1 ],
					self.help[ argSplit[ 1 ] ][ "description" ],
					self.help[ argSplit[ 1 ] ][ "syntax" ] )
				)
			
			else:
				self.privmsg( target, "No help available for '" + 
					argSplit[ 2 ] + "'.'" )

		else:
			self.privmsg( target, "Available commands: " + 
				", ".join( self.help.keys() ) + 
				". For more information type \x03.help <command>\x0f." )
		
		return True

