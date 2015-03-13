# coding: utf-8

from irc.client import NickMask

def on_module_loaded( self ):
    return [ "commands", "cmds" ]

def on_privmsg( self, c, e ):
    do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
    do_command( self, e, e.target )

def do_command( self, e, target ):
    if e.arguments[ 0 ].lower() in [ ".commands", ".cmds" ]:
        self.privmsg( target, [ i for i in self.modulecommands ] )
		
        return True

