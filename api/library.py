import xml.etree.cElementTree as ET
from urllib2 import urlopen

from album import Album

class Library(object):
    
    def __init__(self, library_element, client):
        self.client = client
        self.id = library_element.get('id')
        self.detail = library_element.get('detail')
        self.name = library_element.get('name')

    def get_albums(self):
        album_list = []
        method_url = self.client.webservice_url + '/getalbums/' + self.client.service_token + '/' + self.id
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        albums = root.find('albums').getchildren()

        for album_element in albums:
            album = Album(album_element, self.client)
            album_list.append(album)

        return album_list
