from harvestmedia.api.config import Config
from harvestmedia.api.client import Client
from harvestmedia.api.playlist import Playlist
from harvestmedia.api.member import Member
from harvestmedia.api.track import Track

api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

client = Client(api_key=api_key, debug_level='DEBUG')

member = Member.query.get_by_id('46d6bb0b1a2aafe7', client)
playlists = member.get_playlists()

#playlist = Playlist()
#playlist.member_id = '46d6bb0b1a2aafe7'
#playlist.name = 'test playlist'
#playlist.create()
