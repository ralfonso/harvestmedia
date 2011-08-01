# -*- coding: utf-8 -*-
from util import DictObj
import exceptions
from track import Track
import client


class Album(DictObj):
    
    def __init__(self, xml_data=None, connection=None):
        self.client = connection

        if self.client is None:
            self.client = client.APIClient()

        if xml_data is not None:
            self._load(xml_data)

    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

    def as_dict(self):
        return dict([(k,v) for k,v in self.__dict__.items()])

    def get_tracks(self):
        track_list = []
        method_uri = '/getalbumtracks/%(service_token)s/' + self.id

        xml_root = self.client.get_remote_xml_root(method_uri)
        tracks = xml_root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track(track_element)
            track_list.append(track)

        return track_list
    
    def get_cover_url(self, width=None, height=None):
        asset_url = self.client.config.album_art_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url

