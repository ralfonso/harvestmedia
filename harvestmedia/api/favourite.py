# -*- coding: utf-8 -*-
from .util import DictObj
from .track import Track


class FavoriteQuery(object):

    def add_track(self, member_id, track_id, _client):
        method_uri = '/addtofavourites/{{service_token}}/%(member_id)s/track/%(track_id)s' % \
                        {'member_id': member_id,
                         'track_id': track_id}
        _client.get_xml(method_uri)

    def remove_track(self, member_id, track_id, _client):
        method_uri = '/removefavouritestrack/{{service_token}}/%(member_id)s/%(track_id)s' % \
                        {'member_id': member_id,
                         'track_id': track_id}
        _client.get_xml(method_uri)


class Favourite(DictObj):

    query = FavoriteQuery()

    def __init__(self, _client):
        """ Create a new Favourite object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self._client = _client
        self.tracks = []

    @classmethod
    def from_xml(cls, xml_data, _client):
        instance = cls(_client)

        tracks = xml_data.find('tracks')
        if tracks:
            for track in tracks.getchildren():
                instance.tracks.append(Track.from_xml(track, _client))

        return instance

    def add_track(self, track_id):
        self.query.add_track(self.member_id, self.track_id, self._client)

    def remove_track(self, track_id):
        self.query.remove_track(self.member_id, self.track_id, self._client)
