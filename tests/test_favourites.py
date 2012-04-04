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

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_member_favourites(HttpMock):
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
                                    </memberaccount>""" % \
                                    {'test_member_id': test_member_id,
                                     'username': username,
                                     'firstname': firstname,
                                     'lastname': lastname,
                                     'email': email})
 
    member = Member.from_xml(member_xml, client)

    test_track_id = get_random_md5()
    test_track_name = 'test track'

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
                         <ResponseFavourites>
                            <favourites>
                                <tracks>
                                    <track id="%(id)s" name="%(name)s" />
                                </tracks>
                            </favourites>
                        </ResponseFavourites>""" % {'id': test_track_id,
                                                'name': test_track_name,}


    http = build_http_mock(HttpMock, content=xml_response)
    favourites = member.get_favourites()

    assert isinstance(favourites, list)

    favourite = favourites[0]

    assert favourite.id == test_track_id
    assert favourite.name == test_track_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_add_track(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_track_id = get_random_md5()
    test_track_name = 'test track'

    favourite_xml = ET.fromstring("""<favourites>
                                        <tracks>
                                            <track id="%(id)s" name="%(name)s" />
                                        </tracks>
                                    </favourites>""" % {'id': test_track_id,
                                                        'name': test_track_name,})

    favourites = Favourite.from_xml(favourite_xml, client)

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    test_track_id_add = get_random_md5()

    http = build_http_mock(HttpMock, content=xml_response)
    favourites.add_track(test_track_id_add)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove_track(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_track_id = get_random_md5()
    test_track_name = 'test track'

    favourite_xml = ET.fromstring("""<favourites>
                                        <tracks>
                                            <track id="%(id)s" name="%(name)s" />
                                        </tracks>
                                    </favourites>""" % {'id': test_track_id,
                                                        'name': test_track_name,})

    favourites = Favourite.from_xml(favourite_xml, client)

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    http = build_http_mock(HttpMock, content=xml_response)
    favourites.remove_track(test_track_id)
