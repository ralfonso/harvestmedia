# -*- coding: utf-8 -*-
import pdb
from util import DictObj
import xml.etree.cElementTree as ET
import exceptions
import client
import config


class CategoryQuery(object):

    def get_categories(self, _client):
        categories = []

        method_uri = '/getcategories/{{service_token}}'
        xml_root = _client.get_xml(method_uri)

        xml_categories = xml_root.find('categories').getchildren()
        for xml_category in xml_categories:
            category = Category.from_xml(xml_category, _client)
            categories.append(category)

        return categories


class Attribute(DictObj):
    
    def __init__(self, xml_data=None):
        self.attributes = []

    @classmethod
    def from_xml(cls, xml_data, _client):
        """
        Convert the Harvest Media XML tree to our Attribute object
        """

        instance = cls(_client)
        instance.id = xml_data.get('id')
        name_value = xml_data.get('name')

        if ' - ' in name_value:
            instance.value, instance.name = name_value.split(' - ')
        else:
            instance.name = name_value
            instance.value = None

        _attributes = xml_data.find('attributes')

        if _attributes:
            for attribute_xml in _attributes:
               instance.attributes.append(Attribute.from_xml(attribute_xml, _client))

        return instance


class Category(DictObj):

    query = CategoryQuery()
    
    def __init__(self, _client):
        self._client = _client
        self.attributes = []

    @classmethod
    def from_xml(cls, xml_data, _client):
        """
        Convert the Harvest Media XML tree to our Category object
        """

        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        _attributes = xml_data.find('attributes')

        if _attributes:
            for attribute_xml in _attributes.getchildren():
                instance.attributes.append(Attribute.from_xml(attribute_xml, _client))

        return instance
