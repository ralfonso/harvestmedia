# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging

from util import DictObj
import client

from harvestmedia.api.category import Category

logger = logging.getLogger('harvestmedia')

class Track(DictObj):
    """ Represents a Harvest Media track asset """

    def __init__(self, xml_data, _client):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        self.categories = []
        self._load(xml_data)
        self._client = _client
 
    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

        categories = xml_data.find('categories')
        if categories is not None:
            for category in categories.getchildren():
                self.categories.append(Category(category))

    def as_dict(self):
        return dict([(k, v) for k,v in self.__dict__.items()])


    @classmethod 
    def get_by_id(cls, track_id, _client):
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
                return cls(xml_track, _client)

    @classmethod
    def get_multiple(cls, track_ids, _client):
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
                tracks.append(cls(xml_track, _client))

        return tracks

    def get_waveform_url(self, width=None, height=None):
        asset_url = self._client.config.waveform_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url
