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

from utils import build_http_mock, get_random_md5, init_client


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_missing_username():
    client = init_client()
    member = Member(client)
    member.create()


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_create_member(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    first_name = 'Test'
    last_name = 'User'
    email = 'email@email.com'

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
     <ResponseMember>
        <memberaccount id="%(test_member_id)s">
            <username>%(username)s</username>
            <first_name>%(first_name)s</first_name>
            <last_name>%(last_name)s</last_name>
            <email>%(email)s</email>
        </memberaccount>
    </ResponseMember>""" % {'test_member_id': test_member_id,
                            'username': username,
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email}

    username = username
    first_name = first_name
    last_name = last_name
    email = email
    termsaccept = 'true'
    fileformat = 'MP3'

    http = build_http_mock(HttpMock, content=xml_response)
    member = Member.create(_client=client, username=username, first_name=first_name,
                           last_name=last_name, email=email, termsaccept=termsaccept,
                           fileformat=fileformat)

    assert member.id == test_member_id
    assert member.username == username


def test_from_xml():
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    xml_str = """<memberaccount id="%(test_member_id)s">
                    <username>%(username)s</username>
                    <firstname>%(firstname)s</firstname>
                    <lastname>%(lastname)s</lastname>
                    <email>%(email)s</email>
                </memberaccount>""" % \
                    {'test_member_id': test_member_id,
                     'username': username,
                     'firstname': firstname,
                     'lastname': lastname,
                     'email': email}

    member_xml = ET.fromstring(xml_str)
    member = Member.from_xml(member_xml, client)

    assert member.id == test_member_id
    assert member.firstname == firstname


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_member_update(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_username = 'username'
    test_email = 'test@test.com'
    test_firstname = 'test'
    test_lastname = 'user'
    test_username_update = 'new name'

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponseMember>
                    <memberaccount id="%(test_member_id)s">
                        <username>%(test_username)s</username>
                        <firstname>%(test_firstname)s</firstname>
                        <lastname>%(test_lastname)s</lastname>
                        <email>%(test_email)s</email>
                    </memberaccount>
                </ResponseMember>""" % locals()),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponseMember>
                    <memberaccount id="%(test_member_id)s">
                        <username>%(test_username_update)s</username>
                        <firstname>%(test_firstname)s</firstname>
                        <lastname>%(test_lastname)s</lastname>
                        <email>%(test_email)s</email>
                    </memberaccount>
                </ResponseMember>""" % locals()),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    member = Member.query.get_by_id(test_member_id, client)
    assert member.username == test_username
    member.username = test_username_update
    member.update()
    assert member.username == test_username_update


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_member_authenticate(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_username = 'username'
    test_password = get_random_md5()
    test_firstname = 'first'
    test_lastname = 'last'
    test_email = 'test@test.com'

    content = """<?xml version="1.0" encoding="utf-8"?>
                 <ResponseMember>
                    <memberaccount id="%(test_member_id)s">
                        <username>%(test_username)s</username>
                        <firstname>%(test_firstname)s</firstname>
                        <lastname>%(test_lastname)s</lastname>
                        <email>%(test_email)s</email>
                    </memberaccount>
                </ResponseMember>""" % locals()

    http = build_http_mock(HttpMock, content=content)
    member = Member.authenticate(test_username, test_password, client)
    assert member.id == test_member_id


@raises(harvestmedia.api.exceptions.InvalidLoginDetails)
@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_member_authenticate_fail(HttpMock):
    client = init_client()
    test_username = 'username'
    test_password = get_random_md5()

    content = """<?xml version="1.0" encoding="utf-8"?>
                    <responsemember>
                    <error>
                        <code>6</code>
                        <description>Invalid Login Details</description>
                    </error>
                 </responsemember>"""

    http = build_http_mock(HttpMock, content=content)
    member = Member.authenticate(test_username, test_password, client)


@raises(harvestmedia.api.exceptions.MemberDoesNotExist)
@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_member_invalid(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()

    content = """<?xml version="1.0" encoding="utf-8"?>
                    <responsemember>
                    <error>
                        <code>7</code>
                        <description>Member Does Not Exist</description>
                    </error>
                 </responsemember>"""

    http = build_http_mock(HttpMock, content=content)
    member = Member.query.get_by_id(test_member_id, client)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_send_password(HttpMock):
    client = init_client()
    test_username = 'username'

    content = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    http = build_http_mock(HttpMock, content=content)
    Member.send_password(test_username, client)


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
                                                   'name': test_track_name}

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
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    xml_str = """<memberaccount id="%(test_member_id)s">
                    <username>%(username)s</username>
                    <firstname>%(firstname)s</firstname>
                    <lastname>%(lastname)s</lastname>
                    <email>%(email)s</email>
                </memberaccount>""" % \
                    {'test_member_id': test_member_id,
                     'username': username,
                     'firstname': firstname,
                     'lastname': lastname,
                     'email': email}

    member_xml = ET.fromstring(xml_str)
    member = Member.from_xml(member_xml, client)

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    http = build_http_mock(HttpMock, content=xml_response)
    test_track_id = get_random_md5()
    member.add_favourite(test_track_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove_track(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    xml_str = """<memberaccount id="%(test_member_id)s">
                    <username>%(username)s</username>
                    <firstname>%(firstname)s</firstname>
                    <lastname>%(lastname)s</lastname>
                    <email>%(email)s</email>
                </memberaccount>""" % \
                    {'test_member_id': test_member_id,
                     'username': username,
                     'firstname': firstname,
                     'lastname': lastname,
                     'email': email}

    member_xml = ET.fromstring(xml_str)
    member = Member.from_xml(member_xml, client)

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    http = build_http_mock(HttpMock, content=xml_response)
    test_track_id = get_random_md5()
    member.remove_favourite(test_track_id)
