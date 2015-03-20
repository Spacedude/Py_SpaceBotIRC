# coding: utf-8

from irc.client import NickMask

def on_privmsg( self, c, e ):
    do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
    do_command( self, e, e.target )

def do_command( self, e, target ):
    if e.arguments[ 0 ].lower() == ".bots":
        self.privmsg( target, "Human pls go" )

        return True

