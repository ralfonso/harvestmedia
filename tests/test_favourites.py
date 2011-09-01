
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
from harvestmedia.api.favourite import Favourite

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_member_favourites(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    now = datetime.datetime.today().isoformat()
    test_track_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    test_track_name = 'test track'

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
     <ResponseFavourites>
        <favourites>
            <tracks>
                <track id="%(id)s" name="%(name)s" />
            </tracks>
        </favourites>
    </ResponseFavourites>""" % {'id': test_track_id, 
                            'name': test_track_name,}

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    config = harvestmedia.api.config.Config()
    config.debug = True
    member = Member()
    member.id = test_member_id
    favourites = member.get_favourites()

    assert isinstance(favourites, list)

    favourite = favourites[0]

    assert favourite.id == test_track_id
    assert favourite.name == test_track_name

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_add_track(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_track_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing

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

    favourite = Favourite()
    favourite.member_id = 123
    return_value = favourite.add_track(test_track_id)

    assert return_value


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_remove_track(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_track_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing

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

    favourite = Favourite()
    favourite.member_id = 123
    return_value = favourite.remove_track(test_track_id)

    assert return_value

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_remove_member_id_missing():
    favourite = Favourite()
    favourite.remove_track(123)
    
@raises(harvestmedia.api.exceptions.MissingParameter)
def test_remove_id_missing():
    favourite = Favourite()
    favourite.member_id = 123
    favourite.remove_track(None)
