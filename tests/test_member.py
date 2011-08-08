
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

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

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

    xml_response = """
     <?xml version="1.0" encoding="utf-8"?>
     <ResponseMember>
        <memberaccount ID="%(test_member_id)s">
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

    http.getresponse.return_value = StringIO.StringIO(xml_response)
    member = Member()
    member.username = username
    member.first_name = first_name
    member.last_name = last_name
    member.email = email
    member.create()
