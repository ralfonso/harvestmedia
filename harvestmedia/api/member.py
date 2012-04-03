# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging
import urllib

from util import DictObj
import client
from playlist import Playlist
from favourite import Favourite
from track import Track
from exceptions import HarvestMediaError, MissingParameter

logger = logging.getLogger('harvestmedia')


class Member(DictObj):
    def __init__(self, xml_data=None, _client=None):
        """ Create a new Member object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        if _client:
            self._client = _client

        if xml_data:
            self._load(xml_data)
 
    def _load(self, xml_member):
        self.id = xml_member.get('id')
        for child_element in xml_member.getchildren():
            setattr(self, child_element.tag, child_element.text)

    def create(self, ):
        if not self.username:
            raise MissingParameter('You have to specify a username to register a member')

        root = ET.Element('requestmember')
        member = ET.Element('memberaccount')

        for prop, value in vars(self).items():
            if not prop.startswith('_'):
                el = ET.Element(prop)
                el.text = value
                member.append(el)

        terms = ET.Element('termsaccept')
        terms.text = 'true'
        member.append(terms)

        fileformat = ET.Element('fileformat')
        fileformat.text = 'MP3'
        member.append(fileformat)

        root.append(member)

        method_uri = '/registermember/{{service_token}}'
        xml_post_body = ET.tostring(root)

        xml_data = self._client.post_xml(method_uri, xml_post_body)
        xml_member = xml_data.find('memberaccount')
        self._load(xml_member)

    def update(self):
        root = ET.Element('requestmember')
        member = ET.Element('memberaccount')

        member.set('id', str(self.id))

        for prop, value in vars(self).items():
            if not prop.startswith('_'):
                el = ET.Element(prop)
                el.text = value
                member.append(el)

        root.append(member)

        method_uri = '/updatemember/{{service_token}}'
        xml_post_body = ET.tostring(root)

        xml_data = self._client.post_xml(method_uri, xml_post_body)

        xml_member = xml_data.find('memberaccount')
        self._load(xml_member)
        

    @classmethod
    def authenticate(cls, username, password, _client):
        method_uri = '/authenticatemember/{{service_token}}/%(username)s/%(password)s' % {'username': urllib.quote(username), 'password': urllib.quote(password)}
        xml_root = _client.get_xml(method_uri)

        xml_member = xml_root.find('memberaccount')
        return cls(xml_member, _client)

    @classmethod
    def get_by_id(cls, member_id, _client):
        method_uri = '/getmember/{{service_token}}/%(member_id)s' % {'member_id': member_id}
        xml_data = _client.get_xml(method_uri)
        xml_member = xml_data.find('memberaccount')
        return cls(xml_member, _client)

    @staticmethod
    def send_password(username, _client):
        method_uri = '/sendmemberpassword/{{service_token}}/%(username)s' % {'username': urllib.quote(username)}
        _client.get_xml(method_uri)

    def get_playlists(self):
        method_uri = '/getmemberplaylists/{{service_token}}/%(member_id)s' % { 'member_id': self.id }
        xml_root = self._client.get_xml(method_uri)

        playlists = []
        playlist_elements = xml_root.find('playlists')
        for playlist_element in playlist_elements.getchildren():
            playlist = Playlist(playlist_element, self._client)
            playlist.member_id = self.id
            playlists.append(playlist)

        return playlists

    def get_favourites(self):
        method_uri = '/getfavourites/{{service_token}}/%(member_id)s' % { 'member_id': self.id }

        xml_root = self._client.get_xml(method_uri)

        favourites = []
        favourites_element = xml_root.find('favourites')
        track_elements = favourites_element.find('tracks')
        for track_element in track_elements.getchildren():
            favourite = Track(track_element, self._client)
            favourites.append(favourite)

        return favourites
