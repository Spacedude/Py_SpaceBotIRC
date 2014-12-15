# coding: utf-8

import os
import urllib
import json
import HTMLParser
from irc.client import NickMask

htmlparser = HTMLParser.HTMLParser()

def getNowPlaying( self, user, target, showWasPlaying = False ):
	try:
		lfmuser = self.lastFMAccounts[ user ]
		url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=2&format=json" % ( lfmuser, self.lastFMApiKey )
		
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
				
				tagurl = "http://ws.audioscrobbler.com/2.0/?method=track.getTopTags&artist=%s&track=%s&api_key=%s&format=json" % ( artist, title, self.lastFMApiKey )
				artisttagurl = "http://ws.audioscrobbler.com/2.0/?method=artist.getTopTags&artist=%s&api_key=%s&format=json" % ( artist, self.lastFMApiKey )
				
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
			print Exx
	
	except Exception as Ex:
		print Ex

def on_module_loaded( self ):
	if not hasattr( self, "lastFMAccounts" ):
		if os.path.isfile( "lastfm.json" ):
			lfmAccountFile = open( "lastfm.json", 'r' )
			self.lastFMAccounts = json.load( lfmAccountFile )
			lfmAccountFile.close()
		
		else:
			self.lastFMAccounts = {}
	
	return [ "np", "wp", "account", "compare" ]

def on_privmsg( self, c, e ):
	do_command( self, e, str( e.source.nick ), e.arguments[ 0 ] )

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
		
		if cmd == "account":
			if self.hasPermission( str( e.source.nick ), str( e.target ), 10 ):
				try:
					if len( args ) > 0:
						self.lastFMAccounts[ str( e.source.nick ) ] = args[ 0 ]
						self.notice( str( e.source.nick ), "Last.FM account set to %s" % args[ 0 ] )
						
						lfmAccountFile = open( "lastfm.json", 'w' )
						lfmAccountFile.write( json.dumps( self.lastFMAccounts ) )
						lfmAccountFile.close()
				
				except:
					pass
			
			return True
		
		elif cmd == "np":
			if self.hasPermission( str( e.source.nick ), str( e.target ), 10 ):
				if str( e.source.nick ) in self.lastFMAccounts:
					getNowPlaying( self, str( e.source.nick ), target, True )
			
			return True
		
		elif cmd == "wp":
			if self.hasPermission( str( e.source.nick ), str( e.target ), 10 ):
				if target in self.channels:
					for user in self.channels[ target ].users():
						if str( user ) in self.lastFMAccounts:
							getNowPlaying( self, str( user ), target )
			
			return True
		
		elif cmd == "compare":
			if self.hasPermission( str( e.source.nick ), str( e.target ), 10 ):
				user1 = ""
				user2 = ""
				duser1 = ""
				duser2 = ""

				if len( args ) >= 2:
					user1 = args[ 0 ]
					user2 = args[ 1 ]
				else:
					user1 = str( e.source.nick )
					user2 = args[ 0 ]

				duser1 = user1
				duser2 = user2

				if user1 in self.lastFMAccounts:
					user1 = self.lastFMAccounts[ user1 ]

				if user2 in self.lastFMAccounts:
					user2 = self.lastFMAccounts[ user2 ]

				if user1 != "" and user2 != "":
					try:
						url = "http://ws.audioscrobbler.com/2.0/?method=tasteometer.compare&type1=user&type2=user&value1=%s&value2=%s&limit=5&api_key=%s&format=json" % ( user1, user2, self.lastFMApiKey )
						content = urllib.urlopen( url )
						comparejson = json.load( content )
						result = comparejson[ "comparison" ][ "result" ]
						score = int( float( result[ "score" ] ) * 100 )
						artists = result[ "artists" ][ "artist" ]

						artistsString = ""

						for artist in artists:
							artistsString = artistsString + ", " + artist[ "name" ]

						self.privmsg( target, "Comparison of %s and %s: %s/100 featuring %s" % ( duser1, duser2, score, artistsString[ 2: ] ) )
					except Exception as Ex:
						print "Ex: " + str( Ex )
				else:
					if user1 == "":
						self.notice( str( e.source.nick ), "User 1 is unset" )

					if user2 == "":
						self.notice( str( e.source.nick ), "User 2 is unset" )

			return True
