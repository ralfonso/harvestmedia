# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import logging

from util import DictObj
import client
from exceptions import MissingParameter

logger = logging.getLogger('harvestmedia')

class Member(DictObj):
    def __init__(self, xml_data=None, connection=None):
        """ Create a new Member object from an ElementTree.Element object

        xml_data: the ElementTree.Element object to parse

        """

        self.client = connection
        if self.client is None:
            self.client = client.APIClient()

        if xml_data is not None:
            self._load(xml_data)
 
    def _load(self, xml_member):
        self.id = xml_member.get('id')
        for attribute, value in xml_member.items():
            setattr(self, attribute, value)

    def create(self):
        if not self.username:
            raise MissingParameter('You have to specify a username to register a member')

        root = ET.Element('requestmember')
        member = ET.Element('memberaccount')
        root.append(member)

        for attribute, value in self.__dict__.items():
            if attribute == 'client':
                continue

            attribute_element = ET.Element(attribute)
            attribute_element.text = value
            member.append(attribute_element)

        method_uri = '/registermember/{{service_token}}'
        xml_post_body = ET.tostring(root)

        server_xml = self.client.post_xml(method_uri, xml_post_body)
        xml_data = ET.fromstring(server_xml)
        xml_member = xml_data.find('memberaccount')
        self._load(xml_member)


    def authenticate(self, username, password):
        method_uri = '/authenticatemember/{{service_token}}/%(username)s/%(password)s' % {'username': username, 'password': password}
        xml_root = self.client.get_remote_xml_root(method_uri)

        xml_member = xml_root.find('memberaccount')
        xml_username = xml_member.find('username')

        if xml_username is not None:
            return xml_member.get('id') 
        else:
            return False

    def send_password(self, username):
        method_uri = '/sendmemberpassword/{{service_token}}/%(username)s' % {'username': username}
        xml_root = self.client.get_remote_xml_root(method_uri)
