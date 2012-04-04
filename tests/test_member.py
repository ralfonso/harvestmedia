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

from setup import init_client
from utils import get_random_md5


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
    client = init_client()
    member = Member(client)
    member.create()


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_create_member(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
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
    username = username
    first_name = first_name
    last_name = last_name
    email = email
    termsaccept = 'true'
    fileformat = 'MP3'
    member = Member.create(_client=client, username=username, first_name=first_name,
                           last_name=last_name, email=email, termsaccept=termsaccept,
                           fileformat=fileformat)

    assert member.id == test_member_id
    assert member.username == username


def test_from_xml():
    client = init_client()
    now = datetime.datetime.today().isoformat()
    test_member_id = hashlib.md5(now).hexdigest() # generate an md5 from the date for testing
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

    assert member.id == test_member_id
    assert member.firstname == firstname


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_update(HTTPMock):
    client = init_client()
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

    member = Member.query.get_by_id(test_member_id, client)
    assert member.username == test_username
    member.username = test_username_update
    member.update()
    assert member.username == test_username_update


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_authenticate(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_username = 'username'
    test_password = get_random_md5()
    test_firstname = 'first'
    test_lastname = 'last'
    test_email = 'test@test.com'

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

    member = Member.authenticate(test_username, test_password, client)
    assert member.id == test_member_id


@raises(harvestmedia.api.exceptions.InvalidLoginDetails)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_authenticate_fail(HTTPMock):
    client = init_client()
    test_username = 'username'
    test_password = get_random_md5()

    http = HTTPMock()
    mock_response = StringIO.StringIO('<?xml version="1.0" encoding="utf-8"?><responsemember><error><code>6</code><description>Invalid Login Details</description></error></responsemember>')
    mock_response.status = 200
    http.getresponse.return_value = mock_response

    member = Member.authenticate(test_username, test_password, client)


@raises(harvestmedia.api.exceptions.MemberDoesNotExist)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_member_invalid(HTTPMock):
    client = init_client()
    test_member_id = get_random_md5()

    http = HTTPMock()
    mock_response = StringIO.StringIO('<?xml version="1.0" encoding="utf-8"?><responsemember><error><code>7</code><description>Member Does Not Exist</description></error></responsemember>')
    mock_response.status = 200
    http.getresponse.return_value = mock_response

    member = Member.query.get_by_id(test_member_id, client)


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_send_password(HTTPMock):
    client = init_client()
    test_username = 'username'
    http = HTTPMock()

    xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <code>OK</code>
        </responsecode>"""

    response = HTTPResponseMock()
    response.read_response = xml_response
    http.getresponse.return_value = response
    Member.send_password(test_username, client)
