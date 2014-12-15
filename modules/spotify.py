# coding: utf-8

import os
import json
import urllib
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()

def on_module_loaded( self ):
	if not hasattr( self, "lastFMAccounts" ):
		if os.path.isfile( "lastfm.json" ):
			lfmAccountFile = open( "lastfm.json", 'r' )
			self.lastFMAccounts = json.load( lfmAccountFile )
			lfmAccountFile.close()
		
		else:
			self.lastFMAccounts = {}
	
	return [ "spotify" ]

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
		
		if cmd == "spotify":
			if self.hasPermission( e.source.nick, str( e.target ), 10 ):
				user = None
				player = ""
				
				if arg == "":
					if e.source.nick in self.lastFMAccounts:
						user = self.lastFMAccounts[ e.source.nick ]
						player = e.source.nick
				else:
					user = arg
					player = user
				
				if user != None:
					try:
						playurl = None
						url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=1&format=json" % ( user, self.lastFMApiKey )
						lfmjson = json.load( urllib.urlopen( url ) )
						
						artist = htmlparser.unescape( lfmjson[ "recenttracks" ][ "track" ][ 0 ][ "artist" ][ "#text" ] )
						title = htmlparser.unescape( lfmjson[ "recenttracks" ][ "track" ][ 0 ][ "name" ] )
						
						spotifyurl = "http://ws.spotify.com/search/1/track.json?q=%s %s" % ( artist, title )
						lfmjson = json.load( urllib.urlopen( spotifyurl ) )
						
						for entry in lfmjson[ "tracks" ]:
							if entry[ 'name' ].lower() == title.lower():
								playurl = "http://open.spotify.com/track/%s" % entry[ "href" ].split( ":" )[ 2 ]
								
								self.privmsg( target, "\x02%s\x0F: %s" % ( player, playurl ) )
								
								break
					
					except:
						pass
			
			return True
