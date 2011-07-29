from nose.tools import raises
from unittest.case import SkipTest
from urllib2 import urlopen
import StringIO

import mock
import datetime, md5

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.library import Library

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

@mock.patch('harvestmedia.api.client.urlopen')
@raises(harvestmedia.api.exceptions.InvalidAPIResponse)
def test_xml_failure(urlopen_mock):
    urlopen_mock.return_value = StringIO.StringIO('<xml><this xml is malformed</xml>')

    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()

@mock.patch('harvestmedia.api.client.urlopen')
def test_get_service_token(UrlOpenMock):
    u = UrlOpenMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = md5.md5(expiry).hexdigest() # generate an md5 from the date for testing
    u.read.return_value = '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry)
    
    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()
    
    assert client.service_token == test_token
    assert client.service_token_expires == expiry

@mock.patch('harvestmedia.api.client.urlopen')
def test_get_libraries(UrlOpenMock):
    u = UrlOpenMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = md5.md5(expiry).hexdigest() # generate an md5 from the date for testing
    u.read.return_value = '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry)
    
    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()
    u.read.return_value = """
        <ResponseLibraries>
            <libraries> 
                <library id="abc123" name="VIDEOHELPER" detail="Library description" />
                <library id="abc125" name="MODULES" detail="Library description" />
            </libraries>
        </ResponseLibraries>"""

    libraries = Library.get_libraries()
    assert isinstance(libraries, list)

    library = libraries[0]
    assert library.id == 'abc123'
    assert library.name == 'VIDEOHELPER'
