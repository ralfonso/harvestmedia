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
    """ Represents a Harvest Media category attibute.
    Consists of a name and a collection of sub-attributes

    :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

    """

    def __init__(self, _client):
        self.attributes = []
        self._client = _client

    @classmethod
    def from_xml(cls, xml_data, _client):
        """Internally-used classmethod to recursively convert the Harvest Media XML tree to
        our Attribute object with :class:`Attribute` children.

        Example XML::

            <attribute name="Keyboard" id="da2362b0e30b131f" />
                <attributes>
                    <attribute name="Piano" id="6185334915adc56b" />
                    <attribute name="Organ" id="98098098a0c8" />
              </attributes>                
            </attribute>              

        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

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
    """ Represents a Harvest Media category item.
    Consists of a name and a collection of sub-attributes

    :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

    """

    query = CategoryQuery()

    def __init__(self, _client):
        self._client = _client
        self.attributes = []

    @classmethod
    def from_xml(cls, xml_data, _client):
        """Internally-used classmethod to convert the Harvest Media XML tree to our Category object with
        :class:`Attribute` children.

        Example XML::

            <category name="Instruments" id="098acb89c8bc">
              <attributes>
                <attribute name="Piano" id="da2362b0e30b131f" />
                <attribute name="Drums" id="6185334915adc56b" />
                <attribute name="Guitar" id="98098098a0c8" />
                <attribute name="Bass" id="980a80d98a80c8" />
              </attributes>                
            </category>

        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`
        """

        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        _attributes = xml_data.find('attributes')

        if _attributes:
            for attribute_xml in _attributes.getchildren():
                instance.attributes.append(Attribute.from_xml(attribute_xml, _client))

        return instance
