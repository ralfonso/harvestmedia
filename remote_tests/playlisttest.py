from harvestmedia.api.config import Config
from harvestmedia.api.client import Client
from harvestmedia.api.playlist import Playlist
from harvestmedia.api.member import Member
from harvestmedia.api.track import Track

hmconfig = Config()
hmconfig.api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
hmconfig.api_key = '799b25abdab989c1b1949063476b910954a8a9e74d064f3119f14ef98736a840b058bf34cbec5972'
hmconfig.webservice_url = 'http://betaservice.harvestmedia.net/HMP-WS.svc'
hmconfig.debug = True

member = Member.get_by_id('46d6bb0b1a2aafe7')
playlists = member.get_playlists()

#playlist = Playlist()
#playlist.member_id = '46d6bb0b1a2aafe7'
#playlist.name = 'test playlist'
#playlist.create()
