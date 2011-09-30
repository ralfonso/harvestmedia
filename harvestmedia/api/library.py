# -*- coding: utf-8 -*-
from util import DictObj
import xml.etree.cElementTree as ET
import exceptions
import client
import config
from album import Album


class Library(DictObj):
    
    def __init__(self, xml_data=None, connection=None):
        self._config = config.Config()
        self._client = connection
        if self._client is None:
            self._client = client.APIClient()
            
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

        method_uri = '/getalbums/{{service_token}}/' + self.id
        xml_root = self._client.get_remote_xml_root(method_uri)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album(album_element)
            self.albums[album.id] = album

        return self.albums.values()

    @staticmethod
    def get_libraries(api_client=None):
        libraries = []
        if api_client is None:
            api_client = client.APIClient()

        method_uri = '/getlibraries/{{service_token}}'
        xml_root = api_client.get_remote_xml_root(method_uri)
        xml_libraries = xml_root.find('libraries').getchildren()
        for library_element in xml_libraries:
            library = Library(library_element)
            libraries.append(library)

        return libraries
