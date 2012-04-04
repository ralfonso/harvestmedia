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
from utils import get_random_md5

api_key = '12345'


class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_member_favourites(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    member_xml = """<?xml version="1.0" encoding="utf-8"?>
     <ResponseMember>
        <memberaccount id="%(test_member_id)s">
            <username>%(username)s</username>
            <firstname>%(firstname)s</firstname>
            <lastname>%(lastname)s</lastname>
            <email>%(email)s</email>
        </memberaccount>
    </ResponseMember>""" % {'test_member_id': test_member_id,
                            'username': username,
                            'firstname': firstname,
                            'lastname': lastname,
                            'email': email}

    xml_doc = ET.fromstring(member_xml)
    xml_member = xml_doc.find('memberaccount')

    member = Member.from_xml(xml_member, client)

    test_member_id = get_random_md5()
    test_track_id = get_random_md5()
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
    favourites = member.get_favourites()

    assert isinstance(favourites, list)

    favourite = favourites[0]

    assert favourite.id == test_track_id
    assert favourite.name == test_track_name

@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_add_track(HTTPMock):
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
    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response
    test_track_id_add = get_random_md5()
    favourites.add_track(test_track_id_add)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove_track(HTTPMock):
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

    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    favourites.remove_track(test_track_id)
