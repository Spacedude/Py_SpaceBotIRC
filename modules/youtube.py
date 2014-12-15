# coding: utf-8

import re
import urllib
import json
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()
youtubeRgx = re.compile( r"http(?:s?)://(?:www\.)?youtu(?:be\.com/watch\?v=|\.be/)([\w\-]+)(&(amp;)?[\w\?=‌​]*)?" )

def on_module_loaded( self ):
	return [ "yt" ]

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
		
		if cmd == "yt":
			if self.hasPermission( e.source.nick, str( e.target ), 15 ):
				url = "https://gdata.youtube.com/feeds/api/videos?q=%s&max-results=1&alt=json" % arg
				
				try:
					ytjson = json.load( urllib.urlopen( url ) )
					vidurl = htmlparser.unescape( ytjson[ 'feed' ][ 'entry' ][ 0 ][ 'id' ][ '$t' ] )
					title  = htmlparser.unescape( ytjson[ 'feed' ][ 'entry' ][ 0 ][ 'title' ][ '$t' ] )
					author = htmlparser.unescape( ytjson[ 'feed' ][ 'entry' ][ 0 ][ 'author' ][ 0 ][ 'name' ][ '$t' ] )
					vidurl = "https://youtu.be/" + vidurl[ 42: ]
					
					self.privmsg( target, "\x02\"%s\"\x0F by %s - %s" % ( title, author, vidurl ) )
				
				except Exception as Ex:
					print Ex
					self.privmsg( target, "No results found." )
			
			return True
	
	else:
		for match in youtubeRgx.finditer( arg ):
			if match:
				try:
					url = 'http://gdata.youtube.com/feeds/api/videos/%s?alt=json&v=2' % match.group( 1 )
					ytjson = json.load( urllib.urlopen( url ) )
					title = ytjson[ 'entry' ][ 'title' ][ '$t' ]
					author = ytjson[ 'entry' ][ 'author' ][ 0 ][ 'name' ][ '$t' ]
					
					self.privmsg( target, "\x02\"%s\"\x0F by %s" % ( title, author ) )
				
				except Exception as Ex:
					print Ex
