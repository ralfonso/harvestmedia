from harvestmedia.api.config import Config
from harvestmedia.api.client import Client
from harvestmedia.api.favourite import Favourite
from harvestmedia.api.member import Member
from harvestmedia.api.track import Track

hmconfig = Config()
hmconfig.api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
hmconfig.webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'


hmconfig.api_key = '799b25abdab989c1b1949063476b910954a8a9e74d064f3119f14ef98736a840b058bf34cbec5972'
hmconfig.webservice_url = 'http://betaservice.harvestmedia.net/HMP-WS.svc'
hmconfig.debug = True

member = Member.get_by_id('46d6bb0b1a2aafe7')
favourites = member.get_favourites()

print favourites

favourite = Favourite()
favourite.member_id = '46d6bb0b1a2aafe7'
track_id = '9d91ea10c5707ada'
#favourite.add_track(track_id)
