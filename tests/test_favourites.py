# -*- coding: utf-8 -*-
import datetime
import hashlib
import mock
from nose.tools import raises
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.member import Member
from harvestmedia.api.favourite import Favourite

from setup import init_client

api_key = '12345'


class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_member_favourites(HTTPMock):
    client = init_client()
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
    member = Member(_client=client)
    member.id = test_member_id
    favourites = member.get_favourites()

    assert isinstance(favourites, list)

    favourite = favourites[0]

    assert favourite.id == test_track_id
    assert favourite.name == test_track_name

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_add_track(HTTPMock):
    client = init_client()
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    test_track_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    Favourite.add_track(test_member_id, test_track_id, client)


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_remove_track(HTTPMock):
    client = init_client()
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    test_track_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    Favourite.remove_track(test_member_id, test_track_id, client)
