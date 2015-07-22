# coding: utf-8

import os
import urllib
import json
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()

def getNowPlaying( self, user, target, showWasPlaying = False ):
	try:
		lfmuser = self.data[ "lastfm" ][ "accounts" ][ user ]
		url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=2&format=json" % ( lfmuser, self.data[ "lastfm" ][ "apikey" ] )
		
		lfmjson = json.load( urllib.urlopen( url ) )

		try:
			recenttracks = lfmjson[ "recenttracks" ][ "track" ]

			if len( recenttracks ) == 3:
				isWas = "is"
			else:
				isWas = "was"

			if isWas == "is" or showWasPlaying:
				artist = htmlparser.unescape( recenttracks[ 0 ][ "artist" ][ "#text" ] )
				title = htmlparser.unescape( recenttracks[ 0 ][ "name" ] )
				
				tagurl = "http://ws.audioscrobbler.com/2.0/?method=track.getTopTags&artist=%s&track=%s&api_key=%s&format=json" % ( artist, title, self.data[ "lastfm" ][ "apikey" ] )
				artisttagurl = "http://ws.audioscrobbler.com/2.0/?method=artist.getTopTags&artist=%s&api_key=%s&format=json" % ( artist, self.data[ "lastfm" ][ "apikey"  ] )
				
				toptags = ""

				try:
					tagjson = json.load( urllib.urlopen( tagurl ) )

					try:
						toptags  = htmlparser.unescape( tagjson[ "toptags" ][ "tag" ][ 0 ][ "name" ] )
					except:
						pass

					try:
						toptags += ", " + htmlparser.unescape( tagjson[ "toptags" ][ "tag" ][ 1 ][ "name" ] )
					except:
						pass

					try:
						toptags += ", " + htmlparser.unescape( tagjson[ "toptags" ][ "tag" ][ 2 ][ "name" ] )
					except:
						pass

					if toptags != "":
						toptags = "(%s)" % toptags
				
				except:
					pass

				if toptags == "":
					try:
						artisttagjson = json.load( urllib.urlopen( artisttagurl ) )

						try:
							toptags  = htmlparser.unescape( artisttagjson[ "toptags" ][ "tag" ][ 0 ][ "name" ] )
						except:
							pass

						try:
							toptags += ", " + htmlparser.unescape( artisttagjson[ "toptags" ][ "tag" ][ 1 ][ "name" ] )
						except:
							pass

						try:
							toptags += ", " + htmlparser.unescape( artisttagjson[ "toptags" ][ "tag" ][ 2 ][ "name" ] )
						except:
							pass

						if toptags != None and toptags != "":
							toptags = "(%s)" % toptags
					
					except:
						toptags = ""

				self.privmsg( target, "%s %s playing: %s - %s %s" % ( user, isWas, artist, title, toptags ) )
		
		except Exception as Exx:
			print( Exx )
	
	except Exception as Ex:
		print( Ex )

def on_module_loaded( self ):
	if not "lastfm" in self.data:
		self.data[ "lastfm" ] = {}
	
	if not "accounts" in self.data[ "lastfm" ]:
		self.data[ "lastfm" ][ "accounts" ] = {}
	
	if not "apikey" in self.data[ "lastfm" ]:
		self.data[ "lastfm" ][ "apikey" ] = raw_input( "Please enter your last.fm api key: " )
		self.saveData()

	return {
		"np": {
			"description": "Display what you or someone else is currently listening to.",
			"syntax": ".np [nick|last.fm username]"
		},
		"wp": {
			"description": "Display what everyone in the channel is currently listening to.",
			"syntax": ".wp"
		},
		"account": {
			"description": "Link a last.fm account to your nick.",
			"syntax": ".account <last.fm account name>"
		},
		"compare": {
			"description": "Compare how similar two people's music taste is.",
			"syntax": ".compare <nick|last.fm account> [nick|last.fm account]"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".account":
		arg = " ".join( argSplit[ 1: ] )
		
		if self.hasPermission( e.source.nick, target, 10 ):
			if len( argSplit ) > 1:
				try:
					self.data[ "lastfm" ][ "accounts" ][ str( e.source.nick ) ] = argSplit[ 1 ]
					self.notice( e.source.nick, "Last.FM account set to %s" % argSplit[ 1 ] )
					
					self.saveData()
			
				except:
					pass
		
		return True
		
	elif argSplit[ 0 ] == ".np":
		arg = " ".join( argSplit[ 1: ] )

		if self.hasPermission( e.source.nick, target, 10 ):
			if str( e.source.nick ) in self.data[ "lastfm" ][ "accounts" ]:
				getNowPlaying( self, str( e.source.nick ), target, True )
		
		return True
	
	elif argSplit[ 0 ] == ".wp":
		arg = " ".join( argSplit[ 1: ] )

		if self.hasPermission( e.source.nick, target, 10 ):
			if target in self.channels:
				for user in self.channels[ target ].users():
					if str( user ) in self.data[ "lastfm" ][ "accounts" ]:
						getNowPlaying( self, str( user ), target )
		
		return True
	
	elif argSplit[ 0 ] == ".compare":
		arg = " ".join( argSplit[ 1: ] )
		
		if self.hasPermission( e.source.nick, target, 10 ):
			user1 = ""
			user2 = ""
			duser1 = ""
			duser2 = ""
			
			if len( argSplit ) > 2:
				user1 = argSplit[ 1 ]
				user2 = argSplit[ 2 ]
			else:
				user1 = str( e.source.nick )
				user2 = argSplit[ 1 ]

			duser1 = user1
			duser2 = user2
			
			if user1 in self.data[ "lastfm" ][ "accounts" ]:
				user1 = self.data[ "lastfm" ][ "accounts" ][ user1 ]
			
			if user2 in self.data[ "lastfm" ][ "accounts" ]:
				user2 = self.data[ "lastfm" ][ "accounts" ][ user2 ]
			
			if user1 != "" and user2 != "":
				try:
					url = "http://ws.audioscrobbler.com/2.0/?method=tasteometer.compare&type1=user&type2=user&value1=%s&value2=%s&limit=5&api_key=%s&format=json" % ( user1, user2, self.data[ "lastfm" ][ "apikey" ] )
					content = urllib.urlopen( url )
					comparejson = json.load( content )
					result = comparejson[ "comparison" ][ "result" ]
					
					score = int( float( result[ "score" ] ) * 100 )
					
					try:
						artists = result[ "artists" ][ "artist" ]
						artistsString = ""
					
						for artist in artists:
							artistsString = artistsString + ", " + artist[ "name" ]

					except:
						artistsString = "  no artists"
					
					self.privmsg( target, "Comparison of %s and %s: %s/100 featuring %s" % ( duser1, duser2, score, artistsString[ 2: ] ) )
				
				except Exception as Ex:
					print( "Ex: " + str( Ex ) )

			else:
				if user1 == "":
					self.notice( e.source.nick, "User 1 is unset" )

				if user2 == "":
					self.notice( e.source.nick, "User 2 is unset" )

			return True

