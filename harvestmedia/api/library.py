# -*- coding: utf-8 -*-
from album import Album
from util import DictObj


class LibraryQuery(object):

    def get_libraries(self, _client):
        libraries = []

        method_uri = '/getlibraries/{{service_token}}'
        xml_root = _client.get_xml(method_uri)
        xml_libraries = xml_root.find('libraries').getchildren()
        for library_element in xml_libraries:
            library = Library.from_xml(library_element, _client=_client)
            libraries.append(library)

        return libraries


class Library(DictObj):

    query = LibraryQuery()
    
    def __init__(self ,_client):
        self._client = _client

    @classmethod
    def from_xml(cls, xml_data, _client):
        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        return instance

    def get_albums(self):
        album_list = []
        method_uri = '/getalbums/{{service_token}}/' + self.id
        xml_root = self._client.get_xml(method_uri)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album.from_xml(album_element, _client=self._client)
            album_list.append(album)

        return album_list
