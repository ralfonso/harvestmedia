
# -*- coding: utf-8 -*-
from nose.tools import raises
from unittest.case import SkipTest
from urllib2 import urlopen
import StringIO

import mock
import datetime, hashlib
import xml.etree.cElementTree as ET


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

@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_missing_username():
    member = Member()
    member.create()

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
