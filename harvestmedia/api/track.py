# -*- coding: utf-8 -*-
from util import DictObj
import client


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

    def get_waveform_url(self, width=None, height=None):
        asset_url = self.client.config.waveform_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url
