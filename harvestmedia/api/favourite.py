# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging
from urllib import quote as url_quote

from util import DictObj
import client
from exceptions import MissingParameter

from track import Track

logger = logging.getLogger('harvestmedia')

class Favourite(DictObj):
    def __init__(self, xml_data, _client):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self._client = _client
        self._load(xml_data)
 
    def _load(self, xml_playlist):
        self.id = xml_playlist.get('id')
        for attribute, value in xml_playlist.items():
            setattr(self, attribute, value)

        tracks = xml_playlist.find('tracks')
        if tracks:
            for track in tracks.getchildren():
                self.tracks.append(Track(track, self._client))

    @classmethod
    def add_track(cls, member_id, track_id, _client):
        method_uri = '/addtofavourites/{{service_token}}/%(member_id)s/track/%(track_id)s' % {'member_id': member_id, 'track_id': track_id}
        _client.get_xml(method_uri)
    
    @classmethod
    def remove_track(cls, member_id, track_id, client):
        method_uri = '/removefavouritestrack/{{service_token}}/%(member_id)s/%(track_id)s' % {'member_id': member_id, 'track_id': track_id}
        client.get_xml(method_uri)
