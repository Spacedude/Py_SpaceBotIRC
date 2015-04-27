# coding: utf-8

import re
from irc.client import NickMask
from apiclient.discovery import build
from optparse import OptionParser

youtubeRgx = re.compile( r"http(?:s?)://(?:www\.)?youtu(?:be\.com/watch\?v=|\.be/)([\w\-]+)(&(amp;)?[\w\?=‌​]*)?" )
youtube = None
parser = OptionParser()
parser.add_option( "--q", dest = "q", default = "" )
parser.add_option( "--max-results", dest = "maxResults", default = 1 )
( parseroptions, _args ) = parser.parse_args()

def on_module_loaded( self ):
	global youtube

	if not "youtube" in self.data:
		self.data[ "youtube" ] = {}
	
	if not "apikey" in self.data[ "youtube" ]:
		self.data[ "youtube" ][ "apikey" ] = raw_input( "Please enter your google api key: " )
		self.saveData()
	
	if "apikey" in self.data[ "youtube" ]:
		youtube = build( "youtube", "v3", developerKey = self.data[ "youtube" ][ "apikey" ] )
	
	return {
		"yt": {
			"description": "Search for a certain string on YouTube.",
			"syntax": ".yt <string>"
		}
	}

def on_privmsg( self, c, e ):
	do_command( self, e, e.source.nick )

def on_pubmsg( self, c, e ):
	do_command( self, e, e.target )

def do_command( self, e, target ):
	arg = e.arguments[ 0 ]
	argSplit = arg.split()

	if argSplit[ 0 ] == ".yt":
		arg = " ".join( argSplit[ 1: ] )
		
		if self.hasPermission( e.source.nick, e.target, 15 ):
			try:
				parseroptions.q = arg

				search_response = youtube.search().list(
					q = parseroptions.q,
					part = "id,snippet",
					type = "video",
					maxResults = parseroptions.maxResults
				).execute()
				
				for search_result in search_response.get( "items", [] ):
					if search_result[ "id" ][ "kind" ] == "youtube#video":
						title = search_result[ "snippet" ][ "title" ]
						vidurl = "https://youtu.be/" + search_result[ "id" ][ "videoId" ]
						
						video_response = youtube.videos().list(
							id = search_result[ "id" ][ "videoId" ],
							part = "id,snippet",
							maxResults = 1,
						).execute()

						for video_result in video_response.get( "items", [] ):
							uploader = video_result[ "snippet" ][ "channelTitle" ]
						
							self.privmsg( target, "\x02\"%s\"\x0F by %s - %s" % ( title, uploader, vidurl ) )

							break
						
						break

			except Exception as Ex:
				print( Ex )
				self.privmsg( target, "No results found." )
		
		return True
	
	else:
		for match in youtubeRgx.finditer( arg ):
			if match:
				try:
					video_response = youtube.videos().list(
						id = match.group( 1 ),
						part = "id,snippet",
						maxResults = parseroptions.maxResults,
					).execute()

					for video_result in video_response.get( "items", [] ):
						title = video_result[ "snippet" ][ "title" ]
						uploader = video_result[ "snippet" ][ "channelTitle" ]
						
						self.privmsg( target, "\x02\"%s\"\x0F by %s" % ( title, uploader ) )

						break

				except Exception as Ex:
					print Ex

