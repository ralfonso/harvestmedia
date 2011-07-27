import xml.etree.cElementTree as ET
from urllib2 import urlopen

from library import Library
from album import Album
from track import Track

class Client(object):
    """

    """

    def __init__(self, api_key, webservice_url):
        """
        initialize the Client object

        api_key: the Harvest Media API key to use
        webservice_url: the base Harvest Media API URL
        """

        self.api_key = api_key
        self.webservice_url = webservice_url
        self.libraries = []
        self.albums = {}
        self.albums_by_id = {}
        
        self.get_service_token()

    def get_service_token(self):
        method_url = self.webservice_url + '/getservicetoken/' + self.api_key
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expires')
    
    def get_libraries(self):
        # reset the stored library list
        self.libraries = {}

        method_url = self.webservice_url + '/getlibraries/' + self.service_token
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        libraries = root.find('libraries').getchildren()
        for library_element in libraries:
            library = Library(library_element)
            self.libraries[library.id] = library

        return self.libraries.values()

    def get_library_by_id(self, id, force_reload=False):
        if self.libraries is None or force_reload:
            self.get_libraries()

        return self.libraries[id]


    def get_albums_for_library(self, library_id):
        # reset internal album list
        self.albums[library_id] = {}

        method_url = self.webservice_url + '/getalbums/' + self.service_token + '/' + library_id
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        albums = root.find('albums').getchildren()

        for album_element in albums:
            album = Album(album_element)
            self.albums[library_id][album.id] = album
            self.albums_by_id[album.id] = album

        return self.albums[library_id].values()

    def get_tracks_for_album(self, album_id):
        track_list = []
        method_url = self.webservice_url + '/getalbumtracks/' + self.service_token + '/' + album_id

        xml_file = urlopen(method_url)
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tracks = root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track(track_element)
            track_list.append(track)

        return track_list
