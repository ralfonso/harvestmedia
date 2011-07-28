from util import DictObj
from exceptions import *
from album import Album


class Library(DictObj):
    
    def __init__(self, client, xml_data=None):
        self.client = client
        if xml_data is not None:
            self._load(xml_data)

    def _load(self, xmldata):
        """
        Convert the Harvest Media XML tree to our Library object
        """
        self.id = xmldata.get('id')
        self.detail = xmldata.get('detail')
        self.name = xmldata.get('name')


    def get_albums(self):
        # reset internal album list
        self.albums = {}

        method_url = self.client.webservice_url + '/getalbums/' + self.client.service_token + '/' + self.id
        xml_root = self.client.get_remote_xml_root(method_url)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album(self.client, album_element)
            self.albums[album.id] = album

        return self.albums.values()
