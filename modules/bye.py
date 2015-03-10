# coding: utf-8

import urllib
from irc.client import NickMask

def on_privmsg( self, c, e ):
    do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
    do_command( self, e, e.target )

def do_command( self, e, target ):
    if "bye " + self.data[ "settings" ][ "nickname" ].lower() in e.arguments[ 0 ].lower():
        self.privmsg( target, "Bye " + e.source.nick + "!" )

        return True

