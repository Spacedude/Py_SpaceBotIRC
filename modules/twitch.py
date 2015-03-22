# coding: utf-8

from irc.client import NickMask
import urllib
import json
import threading
import time

def on_module_loaded( self ):
	if not "twitch" in self.data:
		self.data[ "twitch" ] = {}
	
	if not hasattr( self, "twitch" ):
		self.twitch = {}
		self.twitch[ "live" ] = []
	
	if hasattr( self, "twitchthread_stop" ):
		self.twitchthread_stop.set()
	
	if not hasattr( self, "twitchLives" ):
		self.twitchLives = []
	
	self.twitchthread_stop = threading.Event()
	self.twitchthread = threading.Thread( target = streamWatchdog, args = ( self, self.twitchthread_stop ) )
	self.twitchthread.setDaemon( True )
	self.twitchthread.start()

	return {
		"twitch": {
			"description": "Follow or get infos about twitch channels.",
			"syntax": ".twitch <live|follow|unfollow> <channel>"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, c, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, c, e, e.target )

def streamWatchdog( self, stap ):
	counter = 0

	while not stap.is_set():
		time.sleep( 1 )
		counter = counter - 1

		if counter <= 0:
			counter = 60
			
			streamsList = []

			for user, streams in self.data[ "twitch" ].items():
				streamsList = streamsList + streams

			streamsList = list( set( streamsList ) )
			lives = isLive( ",".join( streamsList ) )
			liveNowDict = {}

			for live in lives:
				if not ( live in self.twitchLives ):
					for user, streams in self.data[ "twitch" ].items():
						if live in streams:
							if not user in liveNowDict:
								liveNowDict[ user ] = []

							liveNowDict[ user ].append( live )

			self.twitchLives = lives

			for user, streams in liveNowDict.items():
				if len( streams ) > 1:
					streamsStr = ", ".join( streams[ :-1 ] ) + " and " + streams[ -1 ]

				else:
					streamsStr = streams[ 0 ]

				self.privmsg( user, streamsStr + " just went live!" )

def isLive( chans ):
	liveJson = json.load( urllib.urlopen( "https://api.twitch.tv/kraken/streams/?channel=" + chans ) )
	liveStreams = []
	
	for stream in liveJson[ "streams" ]:
		liveStreams.append( stream[ "channel" ][ "name" ].lower() )

	return liveStreams

def do_command( self, c, e, target ):
	arg = e.arguments[ 0 ].lower()
	argSplit = arg.split()

	if argSplit[ 0 ] == ".twitch":
		if argSplit[ 1 ] == "follow":
			if not e.source.nick in self.data[ "twitch" ]:
				self.data[ "twitch" ][ e.source.nick ] = []

			if argSplit[ 2 ] in self.data[ "twitch" ][ e.source.nick ]:
				self.privmsg( target, "You're already following %s" % argSplit[ 2 ] )
			
			else:
				try:
					argSplit[ 2 ].decode( "ascii" )
				
				except UnicodeDecodeError:
					self.privmsg( target, "No non-ascii chars please" )
				
				else:
					if argSplit[ 2 ] in self.data[ "twitch" ][ e.source.nick ]:
						self.privmsg( target, "You're already following %s" % argSplit[ 2 ] )

					else:
						self.data[ "twitch" ][ e.source.nick ].append( argSplit[ 2 ] )
						self.saveData()

						self.privmsg( target, "You'll now get pm'd when %s starts streaming" % argSplit[ 2 ] )
		
		elif argSplit[ 1 ] == "unfollow":
			if e.source.nick in self.data[ "twitch" ]:
				try:
					self.data[ "twitch" ][ e.source.nick ].remove( argSplit[ 2 ] )
					self.saveData()
					self.privmsg( target, "You won't receive notifications regarding %s anymore" % argSplit[ 2 ] )

				except ValueError:
					self.privmsg( target, "You weren't even following %s but alright" % argSplit[ 2 ] )

			else:
				self.privmsg( target, "You're not even following anyone" )

		elif argSplit[ 1 ] == "live":
			if argSplit[ 2 ] in isLive( argSplit[ 2 ] ):
				self.privmsg( target, argSplit[ 2 ] + " is currently \x039Online" )

			else:
				self.privmsg( target, argSplit[ 2 ] + " is currently \x034Offline" )
		
		else:
			pass

		return True

