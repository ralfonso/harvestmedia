from util import DictObj
from exceptions import *
from track import Track


class Album(DictObj):
    
    def __init__(self, client, xml_data=None):
        self.client = client

        if xml_data is not None:
            self._load(xml_data)

    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

    def as_dict(self):
        return dict([(k,v) for k,v in self.__dict__.items()])

    def get_tracks(self):
        track_list = []
        method_url = self.client.webservice_url + '/getalbumtracks/' + self.client.service_token + '/' + self.id

        xml_root = self.client.get_remote_xml_root(method_url)
        tracks = xml_root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track(self.client, track_element)
            track_list.append(track)

        return track_list
