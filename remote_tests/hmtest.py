import harvestmedia
from harvestmedia.api.config import Config
from harvestmedia.api.library import Library

#dreload(harvestmedia.api.config)
#dreload(harvestmedia.api.client)
#dreload(harvestmedia.api.library)
#dreload(harvestmedia.api.album)

api_key = 'e1d5d645d2d984e499e816a7a314dfbd610149f124c3373455c37ad75ab3ffccf444a04a10953b62'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

hmconfig = Config()
hmconfig.api_key = api_key
hmconfig.webservice_url = webservice_url
hmconfig.debug = True
libraries = Library.get_libraries()

for library in libraries:
    albums = library.get_albums()

for album in albums:
    tracks = album.get_tracks()

for track in tracks:
    print track.name
