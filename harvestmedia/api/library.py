# -*- coding: utf-8 -*-
from album import Album
from util import DictObj


class LibraryQuery(object):
    """Performs calls for the :class:`Library` model, also useful in a static
    context.  Available at `Library.query` or `library_instance.query`

    """

    def get_libraries(self, _client, include_inactive=False):
        """Returns all of the libraries on the configured Harvest Media account

        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        libraries = []

        method_uri = '/getlibraries/{{service_token}}'
        if include_inactive:
            method_uri += '/IncludeInactive'
        xml_root = _client.get_xml(method_uri)
        xml_libraries = xml_root.find('libraries').getchildren()
        for library_element in xml_libraries:
            library = Library._from_xml(library_element, _client=_client)
            libraries.append(library)

        return libraries


    def get_logo_url_for_library(self, library_id, _client, width=None, height=None):
        """Generates a URL that can be used to fetch the
        logo image for a Harvest Media library

        :param library_id: The Harvest Media library identifer
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`
        :param width: optional integer specifiying the width of \
        the image to fetch
        :param height: optional integer specifiying the height of \
        the image to fetch

        """

        asset_url = _client.config.library_logo_url
        asset_url = asset_url.replace('{id}', library_id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url


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

    def get_albums(self, include_inactive=False):
        """Gets all of the albums for this library"""

        return Album.query.get_albums_for_library(self.id, self._client, include_inactive)

    def get_logo_url(self, width, height):
        return self.query.get_logo_url_for_library(self.id, self._client, width, height)
