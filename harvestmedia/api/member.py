# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET


from util import DictObj
import client
from exceptions import MissingParameter


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
 
    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

    def create(self):
        if not self.username:
            raise MissingParameter('You have to specify a username to register a member')

        root = ET.Element('RequestMember')
        member = ET.Element('member')
        root.append(member)

        for attribute, value in self.__dict__.items():
            if attribute == 'client':
                continue

            attribute_element = ET.Element(attribute)
            attribute_element.text = value
            member.append(attribute_element)

        method_uri = '/registermember/%(service_token)s'
        xml_post_body = ET.tostring(root)

        server_xml = self.client.post_xml(method_uri, xml_post_body)
        print server_xml
        xml_data = ET.fromstring(server_xml)
        self._load(xml_data)
