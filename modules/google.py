# coding: utf-8

import re
import urllib
import json
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()

def on_module_loaded( self ):
	return [ "g" ]

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".g":
		arg = " ".join( argSplit[ 1: ] )

		if self.hasPermission( e.source.nick, target, 15 ):
			url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % arg
			
			try:
				googlejson = json.load( urllib.urlopen( url ) )
				content = htmlparser.unescape( googlejson[ "responseData" ][ "results" ][ 0 ][ "content" ] ).replace( "\n", "" ).replace( "<b>", "" ).replace( "</b>", "" )
				title = htmlparser.unescape( googlejson[ "responseData" ][ "results" ][ 0 ][ "title" ] ).replace( "<b>", "" ).replace( "</b>", "" )
				url = googlejson[ "responseData" ][ "results" ][ 0 ][ "unescapedUrl" ]
				
				self.privmsg( target, "\x02%s\x02 - %s - %s" % ( title, content, url ) )
			
			except:
				self.privmsg( target, "No results found." )
		
		return True
