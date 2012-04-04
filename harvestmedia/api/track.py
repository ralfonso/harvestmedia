# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET

from .category import Category
from .util import DictObj


class TrackQuery(object):

    def get_tracks_for_album(self, album_id, _client, get_full_detail=True):
        track_list = []
        method_uri = '/getalbumtracks/{{service_token}}/' + album_id

        xml_root = _client.get_xml(method_uri)
        tracks = xml_root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track.from_xml(track_element, _client)
            track_list.append(track)

        if len(track_list) == 0:
            return track_list

        if get_full_detail:
            # now we need to get the fulldetail
            track_ids = [t.id for t in track_list]
            return self.get_tracks(track_ids, _client)
        else:
            return track_list

    def get_tracks(self, track_ids, _client):
        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')

        for track_id in track_ids:
            xml_track = ET.Element('track')
            xml_track.text = track_id
            xml_data.append(xml_track)

        xml_post_body = ET.tostring(xml_data)

        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_tracks = xml_data.find('tracks')

        tracks = []

        if xml_tracks is not None:
            for xml_track in xml_tracks.getchildren():
                tracks.append(Track.from_xml(xml_track, _client))

        return tracks

    def get_by_id(self, track_id, _client):
        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')
        xml_track = ET.Element('track')
        xml_track.text = track_id
        xml_data.append(xml_track)
        xml_post_body = ET.tostring(xml_data)

        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_tracks = xml_data.find('tracks')
        if xml_tracks is not None:
            xml_track = xml_tracks.find('track')
            if xml_track is not None:
                return Track.from_xml(xml_track, _client)


class Track(DictObj):
    """ Represents a Harvest Media track asset """

    query = TrackQuery()

    def __init__(self, _client):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        self.categories = []
        self._client = _client

    @classmethod
    def from_xml(cls, xml_data, _client):
        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        categories = xml_data.find('categories')
        if categories is not None:
            for category in categories.getchildren():
                instance.categories.append(Category(category))

        return instance

    def as_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items()])

    def get_waveform_url(self, width=None, height=None):
        asset_url = self._client.config.waveform_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url
