from harvestmedia.api.config import Config
from harvestmedia.api.client import Client
from harvestmedia.api.member import Member

api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

client = Client(api_key=api_key, debug_level='DEBUG')

#member = Member(client)
#member.username = 'test123'
#member.email = 'r@weareinstrument.com'
#member.firstname = 'Ryan1'
#member.lastname = 'Roemmich1'
#member.create()

#member = Member(client)
#member.send_password('test')

member = Member(client)
authenticated = member.authenticate('test', 'test', client)
print authenticated

playlists = member.get_playlists()

for playlist in playlists:
    print playlist.id + ': ' + playlist.name
