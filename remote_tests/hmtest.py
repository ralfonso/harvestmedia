import harvestmedia
from harvestmedia.api.config import Config
from harvestmedia.api.library import Library
from harvestmedia.api.client import Client

api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

client = Client(api_key=api_key, debug_level='DEBUG')

libraries = Library.query.get_libraries(client)

for library in libraries:
    albums = library.get_albums()

for album in albums:
    tracks = album.get_tracks()

for track in tracks:
    print track.name
