# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging
from urllib import quote as url_quote

from util import DictObj
import client
from exceptions import MissingParameter

from track import Track

logger = logging.getLogger('harvestmedia')

class Playlist(DictObj):
    def __init__(self, xml_data=None, connection=None):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self.tracks = []

        self.client = connection
        if self.client is None:
            self.client = client.APIClient()

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

    def create(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to create a playlist')

        if not self.name:
            raise MissingParameter('You have to specify a playlist name to create a playlist')

        method_uri = '/addplaylist/{{service_token}}/%(member_id)s/%(playlist_name)s/' % {'member_id': self.member_id, 'playlist_name': url_quote(self.name.encode('utf-8')) }
        xml_root = self.client.get_remote_xml_root(method_uri)
        playlists = xml_root.find('playlists')

        if playlists is not None:
            for playlist in playlists.getchildren():
                name = playlist.get('name')
                if name == self.name:
                    self._load(playlist)

    def add_track(self, track_id):
        method_uri = '/addtoplaylist/{{service_token}}/%(member_id)s/%(playlist_id)s/track/%(track_id)s' % {'member_id': self.member_id, 'playlist_id': self.id, 'track_id': track_id}
        xml_root = self.client.get_remote_xml_root(method_uri)

        response_code = xml_root.find('code')
        status = response_code is not None and response_code.text.lower() == 'ok'

        if status:
            self.tracks.append(Track.get_by_id(track_id))
    
    def remove_track(self, track_id):
        method_uri = '/removeplaylisttrack/{{service_token}}/%(member_id)s/%(playlist_id)s/%(track_id)s' % {'member_id': self.member_id, 'playlist_id': self.id, 'track_id': track_id}
        xml_root = self.client.get_remote_xml_root(method_uri)

        response_code = xml_root.find('code')
        status = response_code is not None and response_code.text.lower() == 'ok'

        if status:
            for track in self.tracks:
                if track.id == track_id:
                    self.tracks.remove(track)

        return status

    def remove(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to remove a playlist')

        if not self.id:
            raise MissingParameter('You have to specify an id to remove a playlist')

        method_uri = '/removeplaylist/{{service_token}}/%(member_id)s/%(id)s' % {'member_id': self.member_id, 'id': self.id}
        xml_root = self.client.get_remote_xml_root(method_uri)

        response_code = xml_root.find('code')
        return response_code is not None and response_code.text.lower() == 'ok'

    def update(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to update a playlist')

        if not self.id:
            raise MissingParameter('You have to specify an id to update a playlist')

        method_uri = '/upateplaylist/{{service_token}}/%(member_id)s/%(playlist_id)s/%(playlist_name)s' % { 'member_id': self.member_id,
                                                                                                            'playlist_id': self.id,
                                                                                                            'playlist_name': url_quote(self.name.encode('utf-8'))}

        xml_root = self.client.get_remote_xml_root(method_uri)

        response_code = xml_root.find('code')
        return response_code is not None and response_code.text.lower() == 'ok'
