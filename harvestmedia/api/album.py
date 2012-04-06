# -*- coding: utf-8 -*-
from track import Track
from util import DictObj


class AlbumQuery(object):

    def get_albums_for_library(self, library_id, _client):
        album_list = []
        method_uri = '/getalbums/{{service_token}}/' + library_id
        xml_root = _client.get_xml(method_uri)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album.from_xml(album_element, _client=_client)
            album_list.append(album)

        return album_list

    def get_cover_url_for_album(self, album_id, _client, width=None, height=None):
        asset_url = _client.config.album_art_url
        asset_url = asset_url.replace('{id}', album_id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url


class Album(DictObj):

    query = AlbumQuery()

    def __init__(self, _client):
        self._client = _client

    def get_tracks(self, get_full_detail=True):
        return Track.query.get_tracks_for_album(self.id, self._client, get_full_detail)

    @classmethod
    def from_xml(cls, xml_data, _client):
        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)
        return instance

    def as_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items()])

    def get_cover_url(self, width=None, height=None):
        return self.query.get_cover_url_for_album(self.id, self._client, width, height)
