# -*- coding: utf-8 -*-
from urllib import quote as url_quote

from .exceptions import MissingParameter
from .track import Track
from .util import DictObj


class PlaylistQuery(object):

    def get_member_playlists(self, member_id, _client):
        method_uri = '/getmemberplaylists/{{service_token}}/%(member_id)s' % \
                        {'member_id': member_id}
        xml_root = _client.get_xml(method_uri)

        playlists = []
        playlist_elements = xml_root.find('playlists')
        for playlist_element in playlist_elements.getchildren():
            playlist = Playlist.from_xml(playlist_element, _client)
            playlist.member_id = member_id
            playlists.append(playlist)

        return playlists

    def add_track(self, member_id, playlist_id, track_id, _client):
        method_uri = '/addtoplaylist/{{u}}/%(member_id)s/%(playlist_id)s/track/%(track_id)s' % \
                          {'member_id': member_id,
                           'playlist_id': id,
                           'track_id': track_id}
        _client.get_xml(method_uri)

    def remove_track(self, member_id, playlist_id, track_id, _client):
        method_uri = '/removeplaylisttrack/{{service_token}}/%(member_id)s/%(playlist_id)s/%(track_id)s' % \
                            {'member_id': member_id,
                             'playlist_id': id,
                             'track_id': track_id}
        _client.get_xml(method_uri)

    def remove(self, member_id, playlist_id, _client):
        method_uri = '/removeplaylist/{{service_token}}/%(member_id)s/%(id)s' % \
                        {'member_id': member_id,
                         'id': id}
        _client.get_xml(method_uri)


class Playlist(DictObj):

    query = PlaylistQuery()

    def __init__(self, _client):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self.tracks = []
        self._client = _client

    @classmethod
    def from_xml(cls, xml_data, _client):
        instance = cls(_client)
        instance.id = xml_data.get('id')
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        tracks = xml_data.find('tracks')
        if tracks:
            for track in tracks.getchildren():
                instance.tracks.append(Track.from_xml(track, _client))

        return instance

    @classmethod
    def create(cls, **kwargs):
        _client = kwargs.get('_client', None)
        if not _client:
            raise MissingParameter('You must pass _client to Playlist.create')

        member_id = kwargs.get('member_id', None)
        if not member_id:
            raise MissingParameter('You must pass member_id to Playlist.create')

        playlist_name = kwargs.get('playlist_name', None)
        if not playlist_name:
            raise MissingParameter('You must pass playlist_name to Playlist.create')

        method_uri = '/addplaylist/{{service_token}}/%(member_id)s/%(playlist_name)s/' % \
                        {'member_id': member_id,
                         'playlist_name': url_quote(playlist_name.encode('utf-8'))}
        xml_root = _client.get_xml(method_uri)
        playlists = xml_root.find('playlists')

        if playlists is not None:
            for playlist_xml in playlists.getchildren():
                name = playlist_xml.get('name')
                if name == playlist_name:
                    return cls.from_xml(playlist_xml, _client)

    def add_track(self, track_id):
        self.query.add_track(self.member_id, self.playlist_id, track_id, self._client)
        self.tracks.append(Track.query.get_by_id(track_id, self._client))

    def remove_track(self, track_id):
        self.query.remove_track(self.member_id, self.id, track_id, self._client)

        for track in self.tracks:
            if track.id == track_id:
                self.tracks.remove(track)

    def remove(self):
        self.query.remove(self.member_id, self.playlist_id, self._client)

    def update(self):
        method_uri = '/updateplaylist/{{service_token}}/%(member_id)s/%(playlist_id)s/%(playlist_name)s' % \
                        {'member_id': self.member_id,
                         'playlist_id': self.id,
                         'playlist_name': url_quote(self.name.encode('utf-8'))}

        self._client.get_xml(method_uri)
        return True
