# -*- coding: utf-8 -*-
from nose.tools import raises, with_setup
from unittest.case import SkipTest
from urllib2 import urlopen
import StringIO

import mock
import datetime, hashlib
import xml.etree.cElementTree as ET

from setup import init_client
from utils import get_random_md5

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.member import Member

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response

@with_setup(init_client)
@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_missing_username():
    member = Member()
    member.create()

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_create_member(HTTPMock):
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    username = 'testuser'
    first_name = 'Test'
    last_name = 'User'
    email = 'email@email.com'

    http = HTTPMock()

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

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response

    config = harvestmedia.api.config.Config()
    config.debug = True
    member = Member()
    member.username = username
    member.first_name = first_name
    member.last_name = last_name
    member.email = email
    member.create()

    assert member.id == test_member_id
    assert member.username == username


def test_load():
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    xml_str = """<?xml version="1.0" encoding="utf-8"?>
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

    xml_doc = ET.fromstring(xml_str)
    xml_member = xml_doc.find('memberaccount')
    member = Member(xml_member)

    assert member.id == test_member_id
    assert member.firstname == firstname

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_update(HTTPMock):
    test_member_id = get_random_md5()
    test_username = 'username'
    test_email = 'test@test.com'
    test_firstname = 'test'
    test_lastname = 'user'
    test_username_update = 'new name'

    http = HTTPMock()

    return_values = [
    """<?xml version="1.0" encoding="utf-8"?>
         <ResponseMember>
            <memberaccount id="%(test_member_id)s">
                <username>%(test_username)s</username>
                <firstname>%(test_firstname)s</firstname>
                <lastname>%(test_lastname)s</lastname>
                <email>%(test_email)s</email>
            </memberaccount>
        </ResponseMember>""" % locals(),
    """<?xml version="1.0" encoding="utf-8"?>
         <ResponseMember>
            <memberaccount id="%(test_member_id)s">
                <username>%(test_username_update)s</username>
                <firstname>%(test_firstname)s</firstname>
                <lastname>%(test_lastname)s</lastname>
                <email>%(test_email)s</email>
            </memberaccount>
        </ResponseMember>""" % locals(),]



    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect

    member = Member.get_by_id(test_member_id)
    assert member.username == test_username
    member.username = test_username_update
    member.update()
    assert member.username == test_username_update

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_authenticate(HTTPMock):
    test_member_id = get_random_md5()
    test_username = 'username'
    test_password = get_random_md5()
    test_email = 'test@test.com'
    test_firstname = 'test'
    test_lastname = 'user'

    http = HTTPMock()

    return_values = [
    """<?xml version="1.0" encoding="utf-8"?>
         <ResponseMember>
            <memberaccount id="%(test_member_id)s">
                <username>%(test_username)s</username>
                <firstname>%(test_firstname)s</firstname>
                <lastname>%(test_lastname)s</lastname>
                <email>%(test_email)s</email>
            </memberaccount>
        </ResponseMember>""" % locals(),]



    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect

    member = Member()
    member.authenticate(test_username, test_password)
    assert member.id == test_member_id

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_send_password(HTTPMock):
    test_username = 'username'
    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response
    member = Member()
    member.send_password(test_username)
