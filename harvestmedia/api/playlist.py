# -*- coding: utf-8 -*-
import logging
from urllib import quote as url_quote

from exceptions import HarvestMediaError, MissingParameter
from track import Track
from util import DictObj

logger = logging.getLogger('harvestmedia')


class Playlist(DictObj):
    def __init__(self, xml_data=None, _client=None):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self.tracks = []

        if _client:
            self._client = _client

        if xml_data:
            self._load(xml_data)
 
    def _load(self, xml_playlist):
        self.id = xml_playlist.get('id')
        for attribute, value in xml_playlist.items():
            setattr(self, attribute, value)

        tracks = xml_playlist.find('tracks')
        if tracks:
            for track in tracks.getchildren():
                self.tracks.append(Track(track, self._client))

    def create(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to create a playlist')

        if not self.name:
            raise MissingParameter('You have to specify a playlist name to create a playlist')

        method_uri = '/addplaylist/{{service_token}}/%(member_id)s/%(playlist_name)s/' % \
                        {'member_id': self.member_id, 
                         'playlist_name': url_quote(self.name.encode('utf-8'))}
        xml_root = self._client.get_xml(method_uri)
        playlists = xml_root.find('playlists')

        if playlists is not None:
            for playlist in playlists.getchildren():
                name = playlist.get('name')
                if name == self.name:
                    self._load(playlist)

    def add_track(self, track_id):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to add a track to a playlist')
        if not self.id:
            raise MissingParameter('You have to specify a playlist id to add a track to a playlist')

        method_uri = '/addtoplaylist/{{service_token}}/%(member_id)s/%(playlist_id)s/track/%(track_id)s' % \
                          {'member_id': self.member_id, 
                           'playlist_id': self.id, 
                           'track_id': track_id}
        self._client.get_xml(method_uri)
        self.tracks.append(Track.get_by_id(track_id, self._client))
    
    def remove_track(self, track_id):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to remove a track from a playlist')
        if not self.id:
            raise MissingParameter('You have to specify a playlist id to remove a track from a playlist')

        method_uri = '/removeplaylisttrack/{{service_token}}/%(member_id)s/%(playlist_id)s/%(track_id)s' % \
                            {'member_id': self.member_id, 
                             'playlist_id': self.id, 
                             'track_id': track_id}
        self._client.get_xml(method_uri)

        for track in self.tracks:
            if track.id == track_id:
                self.tracks.remove(track)

    def remove(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to remove a playlist')
        if not self.id:
            raise MissingParameter('You have to specify a playlist id to remove a playlist')

        method_uri = '/removeplaylist/{{service_token}}/%(member_id)s/%(id)s' % \
                        {'member_id': self.member_id,
                         'id': self.id}
        self._client.get_xml(method_uri)

    def update(self):
        if not self.member_id:
            raise MissingParameter('You have to specify a member_id to update a playlist')
        if not self.id:
            raise MissingParameter('You have to specify an id to update a playlist')

        method_uri = '/updateplaylist/{{service_token}}/%(member_id)s/%(playlist_id)s/%(playlist_name)s' % { 'member_id': self.member_id,
                                                                                                            'playlist_id': self.id,
                                                                                                            'playlist_name': url_quote(self.name.encode('utf-8'))}

        self._client.get_xml(method_uri)
        return True
