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
    def __init__(self, xml_data=None, connection=None):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self._client = connection
        if self._client is None:
            self._client = client.APIClient()

        if xml_data is not None:
            self._load(xml_data)

 
    def _load(self, xml_playlist):
        self.id = xml_playlist.get('id')
        for attribute, value in xml_playlist.items():
            setattr(self, attribute, value)

        tracks = xml_playlist.find('tracks')
        if tracks:
            for track in tracks.getchildren():
                self.tracks.append(Track(track))

    def add_track(self, track_id):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to add to favourites')

        if not track_id:
            raise MissingParameter('You have to specify a track_id to add to favourites')

        method_uri = '/addtofavourites/{{service_token}}/%(member_id)s/track/%(track_id)s' % {'member_id': self.member_id, 'track_id': track_id}
        xml_root = self._client.get_xml(method_uri)

        response_code = xml_root.find('code')
        status = response_code is not None and response_code.text.lower() == 'ok'
        return status

    
    def remove_track(self, track_id):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to add to favourites')

        if not track_id:
            raise MissingParameter('You have to specify a track_id to add to favourites')

        method_uri = '/removefavouritestrack/{{service_token}}/%(member_id)s/%(track_id)s' % {'member_id': self.member_id, 'track_id': track_id}
        xml_root = self._client.get_xml(method_uri)

        response_code = xml_root.find('code')
        status = response_code is not None and response_code.text.lower() == 'ok'

        return status
