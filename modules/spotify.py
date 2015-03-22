# coding: utf-8

import json
import urllib
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()

def on_module_loaded( self ):
	return {
		"spotify": {
			"description": "Output a spotify link to the song you or the specifified person is curently playing.",
			"syntax": ".spotify [nick]"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".spotify":
		arg = " ".join( argSplit[ 1: ] )
		
		if "lastfm" in self.data:
			if "accounts" in self.data[ "lastfm" ]:
				if self.hasPermission( e.source.nick, target, 10 ):
					user = None
					player = ""
					
					if arg == "":
						if e.source.nick in self.data[ "lastfm" ][ "accounts" ]:
							user = self.data[ "lastfm" ][ "accounts" ][ e.source.nick ]
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

