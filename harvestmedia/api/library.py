# -*- coding: utf-8 -*-
from util import DictObj
import xml.etree.cElementTree as ET
import exceptions
import client
import config
from album import Album


class Library(DictObj):
    
    def __init__(self, xml_data, _client):
        self._config = config.Config()
        self._client = _client
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
        xml_root = self._client.get_xml(method_uri)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album(album_element)
            self.albums[album.id] = album

        return self.albums.values()

    @staticmethod
    def get_libraries(_client=None):
        libraries = []

        method_uri = '/getlibraries/{{service_token}}'
        xml_root = _client.get_xml(method_uri)
        xml_libraries = xml_root.find('libraries').getchildren()
        for library_element in xml_libraries:
            library = Library(library_element, _client=_client)
            libraries.append(library)

        return libraries
