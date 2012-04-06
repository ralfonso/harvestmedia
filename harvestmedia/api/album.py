# -*- coding: utf-8 -*-
from track import Track
from util import DictObj


class AlbumQuery(object):
    """Performs calls for the :class:`Album` model, also useful in a static
    context.  Available at `Album.query` or `album_instance.query`

    """


    def get_albums_for_library(self, library_id, _client):
        """Gets all of the albums for a particular library.

        :param library_id: The Harvest Media library identifer
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        album_list = []
        method_uri = '/getalbums/{{service_token}}/' + library_id
        xml_root = _client.get_xml(method_uri)
        albums = xml_root.find('albums').getchildren()

        for album_element in albums:
            album = Album._from_xml(album_element, _client=_client)
            album_list.append(album)

        return album_list

    def get_cover_url_for_album(self, album_id, _client, width=None, height=None):
        """Generates a URL that can be used to fetch the
        cover image for an album on Harvest Media

        :param library_id: The Harvest Media library identifer
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`
        :param width: optional integer specifiying the width of \
        the image to fetch
        :param height: optional integer specifiying the height of \
        the image to fetch

        """

        asset_url = _client.config.album_art_url
        asset_url = asset_url.replace('{id}', album_id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url


class Album(DictObj):
    """ Represents a Harvest Media album asset

    :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

    """


    query = AlbumQuery()

    def __init__(self, _client):
        self._client = _client

    def get_tracks(self, get_full_detail=True):
        """Gets all of the tracks for a this album.

        :param get_full_detail: if True, sends a second request to get all of \
        the details for every track on the album

        """

        return Track.query.get_tracks_for_album(self.id, self._client, get_full_detail)

    @classmethod
    def _from_xml(cls, xml_data, _client):
        """Internally-used classmethod to create an instance of :class:`Album` from
        the XML returned by Harvest Media. Converts all attributes 
        on the node to instance properties.

        Example XML::

            <album featured="false" code="HM001" detail="album description"
                name="Sample Album" displaytitle="Sample Album " id="809a809a8b8ab81" />

        :param xml_data: The Harvest Media XML node
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """
        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)
        return instance

    def as_dict(self):
        """Returns the dictionary representation of this Track"""
        return dict([(k, v) for k, v in self.__dict__.items()])

    def get_cover_url(self, width=None, height=None):
        """Generates a URL that can be used to fetch the
        cover image for this album on Harvest Media

        :param width: optional integer specifiying the width of \
        the image to fetch

        """

        return self.query.get_cover_url_for_album(self.id, self._client, width, height)
