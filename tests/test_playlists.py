# -*- coding: utf-8 -*-
import datetime
import hashlib
from nose.tools import raises, with_setup
import mock
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.member import Member
from harvestmedia.api.playlist import Playlist

from setup import init_client
from utils import get_random_md5

api_key = '12345'

class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_create_playlist(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
     <ResponsePlaylists>
        <playlists>
            <playlist id="%(id)s" name="%(name)s" />
        </playlists>
    </ResponsePlaylists>""" % {'id': test_playlist_id, 
                            'name': test_playlist_name,}

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    playlist = Playlist(_client=client)
    playlist.member_id = test_member_id
    playlist.name = test_playlist_name
    playlist.create()

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name

 
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_member_playlists(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    member_xml = ET.fromstring("""<memberaccount id="%(test_member_id)s">
                                    <username>%(username)s</username>
                                    <firstname>%(firstname)s</firstname>
                                    <lastname>%(lastname)s</lastname>
                                    <email>%(email)s</email>
                                </memberaccount>""" % {'test_member_id': test_member_id, 
                                                       'username': username,
                                                       'firstname': firstname,
                                                       'lastname': lastname,
                                                       'email': email})
    now = datetime.datetime.today().isoformat()
    test_member_id = get_random_md5()
    now = datetime.datetime.today().isoformat()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
     <ResponsePlaylists>
        <playlists>
            <playlist id="%(id)s" name="%(name)s">
                <tracks>
                    <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM" name="Guerilla Pop" id="17376d36f309f18d" keywords="" lyrics="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                </tracks>
            </playlist>
        </playlists>
    </ResponsePlaylists>""" % {'id': test_playlist_id, 
                            'name': test_playlist_name,}

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    member = Member(member_xml, client)
    playlists = member.get_playlists()

    assert isinstance(playlists, list)

    playlist = playlists[0]

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_id_missing():
    playlist = Playlist()
    playlist.create()

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_name_missing():
    playlist = Playlist()
    playlist.member_id = 123
    playlist.create()
    

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_add_track(HTTPMock):
    client = init_client()
    now = datetime.datetime.today().isoformat()
    test_playlist_id = get_random_md5()
    track_id = get_random_md5()

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    playlist = Playlist(_client=client)
    playlist.member_id = 123
    playlist.id = test_playlist_id
    playlist.add_track(track_id)


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_remove(HTTPMock):
    client = init_client()
    now = datetime.datetime.today().isoformat()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    playlist = Playlist(_client=client)
    playlist.remove()


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_remove_track(HTTPMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'

    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    now = datetime.datetime.today().isoformat()
    test_playlist_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    test_playlist_name = 'test playlist'
    track_id = '17376d36f309f18d'

    http = HTTPMock()

    return_values = [
        """<?xml version="1.0" encoding="utf-8"?>
         <ResponsePlaylists>
            <playlists>
                <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                    <tracks>
                        <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM" name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                    </tracks>
                </playlist>
            </playlists>
        </ResponsePlaylists>""" % locals(),
        """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>""",]

    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlists[0].remove_track(track_id)


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_playlist_update(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    test_playlist_update_name = 'test playlist update'
    track_id = '17376d36f309f18d'

    http = HTTPMock()

    return_values = [
        """<?xml version="1.0" encoding="utf-8"?>
         <ResponsePlaylists>
            <playlists>
                <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                    <tracks>
                        <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM" name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                    </tracks>
                </playlist>
            </playlists>
        </ResponsePlaylists>""" % locals(),
        """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>""",]

    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlist = playlists[0]

    playlist.name = test_playlist_update_name
    playlist.update()
    assert playlist.name == test_playlist_update_name


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_playlist_update_missing_id():
    playlist = Playlist()
    playlist.member_id = get_random_md5()
    playlist.update()


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_playlist_update_missing_member_id():
    playlist = Playlist()
    playlist.id = get_random_md5()
    playlist.update()
