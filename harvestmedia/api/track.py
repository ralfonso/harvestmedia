# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging

from util import DictObj
import client


logger = logging.getLogger('harvestmedia')

class Track(DictObj):
    """ Represents a Harvest Media track asset """

    def __init__(self, xml_data=None, connection=None):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        self.client = connection
        if self.client is None:
            self.client = client.APIClient()

        if xml_data is not None:
            self._load(xml_data)
 
    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

    def as_dict(self):
        return dict([(k, v) for k,v in self.__dict__.items()])


    @classmethod 
    def get_by_id(cls, track_id):
        connection = client.APIClient()
        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')
        xml_track = ET.Element('track')
        xml_track.text = track_id
        xml_data.append(xml_track)
        xml_post_body = ET.tostring(xml_data)

        server_xml = connection.post_xml(method_uri, xml_post_body)
        xml_data = ET.fromstring(server_xml)
        xml_tracks = xml_data.find('tracks')
        if xml_tracks is not None:
            xml_track = xml_tracks.find('track')
            if xml_track is not None:
                return cls(xml_track)

    @classmethod
    def get_multiple(cls, track_ids):
        connection = client.APIClient()
        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')

        for track_id in track_ids:
            xml_track = ET.Element('track')
            xml_track.text = track_id
            xml_data.append(xml_track)

        xml_post_body = ET.tostring(xml_data)

        server_xml = connection.post_xml(method_uri, xml_post_body)
        xml_data = ET.fromstring(server_xml)
        xml_tracks = xml_data.find('tracks')

        tracks = []

        if xml_tracks is not None:
            for xml_track in xml_tracks.getchildren():
                tracks.append(cls(xml_track))

        return tracks

    def get_waveform_url(self, width=None, height=None):
        asset_url = self.client.config.waveform_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url
