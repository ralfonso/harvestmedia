# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET

from .category import Category
from .exceptions import MissingParameter
from .util import DictObj

import exceptions


class TrackQuery(object):
    """Performs calls for the :class:`Track` model, also useful in a static
    context.  Available at `Track.query` or `track_instance.query`

    """

    def get_tracks_for_album(self, album_id, _client, get_full_detail=True, include_inactive=False):
        """Gets all of the tracks for a particular album.

        :param album_id: The Harvest Media album identifer
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`
        :param get_full_detail: if True, sends a second request to get all of \
        the details for every track on the album

        """

        track_list = []
        method_uri = '/getalbumtracks/{{service_token}}/' + album_id
        if include_inactive:
            method_uri += '/IncludeInactive'

        xml_root = _client.get_xml(method_uri)
        tracks = xml_root.find('tracks').getchildren()

        for track_element in tracks:
            track = Track._from_xml(track_element, _client)
            track_list.append(track)

        if len(track_list) == 0:
            return track_list

        if get_full_detail:
            # now we need to get the fulldetail
            track_ids = [t.id for t in track_list]
            return self.get_tracks(track_ids, _client)
        else:
            return track_list

    def get_tracks(self, track_ids, _client):
        """Takes a list of track ids and returns a list of
        :class:`harvestmedia.api.track.Track` objects.

        :param track_ids: A list of track identifiers to fetch from Harvest
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')

        for track_id in track_ids:
            xml_track = ET.Element('track')
            xml_track.text = track_id
            xml_data.append(xml_track)

        xml_post_body = ET.tostring(xml_data)

        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_tracks = xml_data.find('tracks')

        tracks = []

        if xml_tracks is not None:
            for xml_track in xml_tracks.getchildren():
                tracks.append(Track._from_xml(xml_track, _client))

        return tracks

    def get_by_id(self, track_id, _client):
        """Takes takes a single track id and returns a
        :class:`harvestmedia.api.track.Track` object.

        :param track_ids: A list of track identifiers to fetch from Harvest
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        method_uri = '/gettracks/{{service_token}}'
        xml_data = ET.Element('tracks')
        xml_data.set('fulldetail', 'true')
        xml_track = ET.Element('track')
        xml_track.text = track_id
        xml_data.append(xml_track)
        xml_post_body = ET.tostring(xml_data)

        xml_data = _client.post_xml(method_uri, xml_post_body)
        xml_tracks = xml_data.find('tracks')
        if xml_tracks is not None:
            xml_track = xml_tracks.find('track')
            if xml_track is not None:
                return Track._from_xml(xml_track, _client)

    def get_track_download_url(self, track_id, track_format, _client, member_id=None, is_master=False):
        format_identifier = _client.config.get_format_identifier(track_format, is_master=is_master)
        if format_identifier is None:
            raise MissingParameter('Invalid track format')

        download_url = _client.config.download_url
        download_url = download_url.replace('{id}', track_id)
        download_url = download_url.replace('{trackformat}', format_identifier)
        if member_id is not None:
            download_url = download_url.replace('{memberaccountid}', member_id)

        return download_url


class Track(DictObj):
    """ Represents a Harvest Media track asset

    :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

    """

    query = TrackQuery()

    def __init__(self, _client):

        self.categories = []
        self._client = _client

    @classmethod
    def _from_xml(cls, xml_data, _client):
        """Internally-used classmethod to create an instance of :class:`Track` from
        the XML returned by Harvest Media. Converts all attributes 
        on the node to instance properties.

        Example XML::

            <track tracknumber="1" time="02:50" lengthseconds="170"
                comment="Track Comment" composer="JJ Jayjay"
                publisher="PP Peepee" name="Epic Track" albumid="1abcbacbac33" id="11bacbcbabcb3b2823"
                displaytitle="Epic Track" genre="Pop / Rock"
                bpm="100" mixout="FULL" frequency="44100" bitrate="1411"
                dateingested="2008-05-15 06:08:18"/>

        :param xml_data: The Harvest Media XML node
        :param _client: An initialized instance of :class:`harvestmedia.api.client.Client`

        """

        instance = cls(_client)
        for attribute, value in xml_data.items():
            setattr(instance, attribute, value)

        categories = xml_data.find('categories')
        if categories is not None:
            for category in categories.getchildren():
                instance.categories.append(Category._from_xml(category, _client=_client))

        return instance

    def as_dict(self):
        """Returns the dictionary representation of this Track"""

        return dict([(k, v) for k, v in self.__dict__.items()])

    def get_waveform_url(self, width=None, height=None):
        """Generates a URL that can be used to fetch the
        waveform image of this track from Harvest Media

        :param width: optional integer specifiying the width of \
        the image to fetch
        :param height: optional integer specifiying the height of \
        the image to fetch

        """

        asset_url = self._client.config.waveform_url
        asset_url = asset_url.replace('{id}', self.id)
        if width:
            asset_url = asset_url.replace('{width}', str(width))
        if height:
            asset_url = asset_url.replace('{height}', str(height))
        return asset_url

    def get_download_url(self, track_format, member_id=None, is_master=False):
        return self.query.get_track_download_url(self.id, track_format, self._client, member_id, is_master)
