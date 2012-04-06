# -*- coding: utf-8 -*-
from album import Album
from util import DictObj


class LibraryQuery(object):
    """Performs calls for the :class:`Library` model, also useful in a static
    context.  Available at `Library.query` or `library_instance.query`

    """

    def get_libraries(self, _client):
        """Returns all of the libraries on the configured Harvest Media account

        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        libraries = []

        method_uri = '/getlibraries/{{service_token}}'
        xml_root = _client.get_xml(method_uri)
        xml_libraries = xml_root.find('libraries').getchildren()
        for library_element in xml_libraries:
            library = Library._from_xml(library_element, _client=_client)
            libraries.append(library)

        return libraries


class Library(DictObj):

    query = LibraryQuery()

    def __init__(self, _client):
        self._client = _client

    @classmethod
    def _from_xml(cls, xml_data, _client):
        """Internally-used classmethod to create an instance of :class:`Library` from
        the XML returned by Harvest Media. Converts all attributes 
        on the node to instance properties.

        Example XML::

            <library id="abc123" name="Sample Library" detail="Library description" />

        :param xml_data: The Harvest Media XML node
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """
        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        return instance

    def get_albums(self):
        """Gets all of the albums for this library"""

        return Album.query.get_albums_for_library(self.id, self._client)
