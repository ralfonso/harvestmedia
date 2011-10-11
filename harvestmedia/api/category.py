# -*- coding: utf-8 -*-
import pdb
from util import DictObj
import xml.etree.cElementTree as ET
import exceptions
import client
import config


class Attribute(DictObj):
    
    def __init__(self, xml_data=None, connection=None):
        self._config = config.Config()
        self._client = connection
        if self._client is None:
            self._client = client.APIClient()
            
        if xml_data is not None:
            self._load(xml_data)

    def _load(self, xmldata):
        """
        Convert the Harvest Media XML tree to our Attribute object
        """
        self.id = xmldata.get('id')
        name_value = xmldata.get('name')
        if ' - ' in name_value:
            self.value, self.name = name_value.split(' - ')
        else:
            self.name = name_value
            self.value = None

        self.attributes = []

        _attributes = xmldata.find('attributes')

        if _attributes:
            for attribute_xml in _attributes:
                self.attributes.append(Attribute(attribute_xml))


class Category(DictObj):
    
    def __init__(self, xml_data=None, connection=None):
        self._config = config.Config()
        self._client = connection
        if self._client is None:
            self._client = client.APIClient()
            
        if xml_data is not None:
            self._load(xml_data)

    def _load(self, xmldata):
        """
        Convert the Harvest Media XML tree to our Category object
        """
        self.id = xmldata.get('id')
        self.name = xmldata.get('name')
        self.attributes = []

        _attributes = xmldata.find('attributes')

        if _attributes:
            for attribute_xml in _attributes.getchildren():
                self.attributes.append(Attribute(attribute_xml))

    @staticmethod
    def get_categories(api_client=None):
        categories = []
        if api_client is None:
            api_client = client.APIClient()

        method_uri = '/getcategories/{{service_token}}'
        xml_root = api_client.get_xml(method_uri)

        xml_categories = xml_root.find('categories').getchildren()
        for xml_category in xml_categories:
            category = Category(xml_category)
            categories.append(category)

        return categories
