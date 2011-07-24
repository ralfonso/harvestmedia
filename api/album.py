import xml.etree.cElementTree as ET
from urllib2 import urlopen

from track import Track

class Album(object):
    
    def __init__(self, album_element, client):
        self.client = client
        for attribute, value in album_element.items():
            setattr(self, attribute, value)

    def get_tracks(self):
        track_list = []
        method_url = self.client.webservice_url + '/getalbumtracks/' + self.client.service_token + '/' + self.id
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        tracks = root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track(track_element, self.client)
            track_list.append(track)

        return track_list
