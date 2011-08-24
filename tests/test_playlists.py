
# -*- coding: utf-8 -*-
from nose.tools import raises
from unittest.case import SkipTest
from urllib2 import urlopen
import StringIO

import mock
import datetime, hashlib

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.member import Member
from harvestmedia.api.playlist import Playlist

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_missing_username():
    member = Member()
    member.create()

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_create_playlist(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    now = datetime.datetime.today().isoformat()
    test_playlist_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
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

    config = harvestmedia.api.config.Config()
    config.debug = True
    playlist = Playlist()
    playlist.member_id = test_member_id
    playlist.name = test_playlist_name
    playlist.create()

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name

 
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_member_playlists(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    now = datetime.datetime.today().isoformat()
    test_playlist_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
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

    config = harvestmedia.api.config.Config()
    config.debug = True
    member = Member()
    member.id = test_member_id
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
def test_remove(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_playlist_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    config = harvestmedia.api.config.Config()
    config.debug = True

    playlist = Playlist()
    playlist.member_id = 123
    playlist.id = test_playlist_id
    return_value = playlist.remove()

    assert return_value

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_remove_member_id_missing():
    playlist = Playlist()
    playlist.remove()
    
@raises(harvestmedia.api.exceptions.MissingParameter)
def test_remove_id_missing():
    playlist = Playlist()
    playlist.member_id = 123
    playlist.remove()
