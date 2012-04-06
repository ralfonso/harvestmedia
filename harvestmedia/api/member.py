# -*- coding: utf-8 -*-
import urllib
import xml.etree.cElementTree as ET

from .exceptions import MissingParameter
from .playlist import Playlist
from .track import Track
from .util import DictObj


class MemberQuery(object):

    def get_by_id(self, member_id, _client):
        method_uri = '/getmember/{{service_token}}/%(member_id)s' % {'member_id': member_id}
        xml_data = _client.get_xml(method_uri)
        xml_member = xml_data.find('memberaccount')
        return Member._from_xml(xml_member, _client)

    def add_favourite(self, member_id, track_id, _client):
        method_uri = '/addtofavourites/{{service_token}}/%(member_id)s/track/%(track_id)s' % \
                        {'member_id': member_id,
                         'track_id': track_id}
        _client.get_xml(method_uri)

    def remove_favourite(self, member_id, track_id, _client):
        method_uri = '/removefavouritestrack/{{service_token}}/%(member_id)s/%(track_id)s' % \
                        {'member_id': member_id,
                         'track_id': track_id}
        _client.get_xml(method_uri)

    def update_member(self, member_id, _client, **kwargs):
        root = ET.Element('requestmember')
        member = ET.Element('memberaccount')

        member.set('id', str(member_id))

        for prop, value in kwargs.items():
            if not prop.startswith('_'):
                el = ET.Element(prop)
                el.text = value
                member.append(el)

        root.append(member)

        method_uri = '/updatemember/{{service_token}}'
        xml_post_body = ET.tostring(root)

        # if this is successful, we can just use the current object
        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_member = xml_data.find('memberaccount')
        return Member._from_xml(xml_member, _client)


class Member(DictObj):

    query = MemberQuery()

    def __init__(self, _client):
        """ Create a new Member object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self._client = _client

    @classmethod
    def _from_xml(cls, xml_member, _client):
        instance = cls(_client)
        instance.id = xml_member.get('id')
        for child_element in xml_member.getchildren():
            setattr(instance, child_element.tag, child_element.text)

        return instance

    @classmethod
    def create(cls, **kwargs):
        _client = kwargs.get('_client', None)
        if not _client:
            raise MissingParameter('You must pass _client to Member.create')

        root = ET.Element('requestmember')
        member = ET.Element('memberaccount')

        for prop, value in kwargs.items():
            if not prop.startswith('_'):
                el = ET.Element(prop)
                el.text = value
                member.append(el)

        root.append(member)

        method_uri = '/registermember/{{service_token}}'
        xml_post_body = ET.tostring(root)

        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_member = xml_data.find('memberaccount')
        return cls._from_xml(xml_member, _client)

    def update(self):
        update_vars = vars(self).copy()
        for k, v in update_vars.items():
            if k.startswith('_'):
                del update_vars[k]
        return self.query.update_member(self.id, self._client, **update_vars)

    @classmethod
    def authenticate(cls, username, password, _client):
        method_uri = '/authenticatemember/{{service_token}}/%(username)s/%(password)s' % \
                        {'username': urllib.quote(username),
                         'password': urllib.quote(password)}
        xml_root = _client.get_xml(method_uri)

        xml_member = xml_root.find('memberaccount')
        return Member._from_xml(xml_member, _client)

    @staticmethod
    def send_password(username, _client):
        method_uri = '/sendmemberpassword/{{service_token}}/%(username)s' % \
                        {'username': urllib.quote(username)}
        _client.get_xml(method_uri)

    def get_playlists(self):
        return Playlist.query.get_member_playlists(self.id, self._client)

    def get_favourites(self):
        method_uri = '/getfavourites/{{service_token}}/%(member_id)s' % \
                        {'member_id': self.id}

        xml_root = self._client.get_xml(method_uri)

        favourites = []
        favourites_element = xml_root.find('favourites')
        track_elements = favourites_element.find('tracks')
        for track_element in track_elements.getchildren():
            favourite = Track._from_xml(track_element, self._client)
            favourites.append(favourite)

        return favourites

    def add_favourite(self, track_id):
        self.query.add_favourite(self.member_id, track_id, self._client)

    def remove_favourite(self, track_id):
        self.query.remove_favourite(self.member_id, track_id, self._client)
