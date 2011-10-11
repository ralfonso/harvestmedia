# -*- coding: utf-8 -*-
from nose.tools import raises
from unittest.case import SkipTest
from urllib2 import urlopen
import StringIO

import mock
import iso8601
import datetime, hashlib

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.library import Library

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
@raises(harvestmedia.api.exceptions.InvalidAPIResponse)
def test_xml_failure(HTTPMock):
    http = HTTPMock()
    mock_response = StringIO.StringIO('<xml><this xml is malformed</xml>')
    mock_response.status = 200
    http.getresponse.return_value = mock_response

    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_service_token(HTTPMock):
    expiry = datetime.datetime.today().isoformat()
    test_token = hashlib.md5(expiry).hexdigest() # generate an md5 from the date for testing

    return_values = [
                     '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry),
                     """<?xml version="1.0" encoding="utf-8"?>
                        <responseserviceinfo>
                            <asseturl
                                albumart="http://asset.harvestmedia.net/albumart/8185d768cd8fcaa7/{id}/{width}/{height}"
                                waveform="http://asset.harvestmedia.net/waveform/8185d768cd8fcaa7/{id}/{width}/{height}" 
                                trackstream="http://asset.harvestmedia.net/trackstream/8185d768cd8fcaa7/{id}" 
                                trackdownload=" http://asset.harvestmedia.net/trackdownload/8185d768cd8fcaa7/{id}/{trackformat}" /> 
                            <trackformats>
                              <trackformat identifier="8185d768cd8fcaa7" extension="mp3" bitrate="320" samplerate="48" samplesize="16" /> 
                              <trackformat identifier="768cd8fcaa8185d7" extension="wav" bitrate="1536" samplerate="48" samplesize="16" /> 
                              <trackformat identifier="7jsi8fcaa818df57" extension="aif" bitrate="1536" samplerate="48" samplesize="16" /> 
                            </trackformats>
                        </responseserviceinfo>""",
                    ]
                        
    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect
    
    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()
    
    assert client.config.service_token == test_token
    assert client.config.service_token_expires == iso8601.parse_date(expiry)

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_libraries(HTTPMock):
    http = HTTPMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = hashlib.md5(expiry).hexdigest() # generate an md5 from the date for testing
    http.getresponse.return_value = StringIO.StringIO('<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry))
    
    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()
    mock_response = StringIO.StringIO("""
        <ResponseLibraries>
            <libraries> 
                <library id="abc123" name="VIDEOHELPER" detail="Library description" />
                <library id="abc125" name="MODULES" detail="Library description" />
            </libraries>
        </ResponseLibraries>""")
    mock_response.status = 200
    http.getresponse.return_value = mock_response

    libraries = Library.get_libraries()
    assert isinstance(libraries, list)

    library = libraries[0]
    assert library.id == 'abc123'
    assert library.name == 'VIDEOHELPER'

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
@raises(harvestmedia.api.exceptions.InvalidToken)
def test_invalid_token(HTTPMock):
    http = HTTPMock()
    mock_response = StringIO.StringIO('<?xml version="1.0" encoding="utf-8"?><memberaccount><error><code>5</code><description>Invalid Token</description></error></memberaccount>')
    mock_response.status = 200
    http.getresponse.return_value = mock_response
    hmconfig = harvestmedia.api.config.Config()
    hmconfig.api_key = api_key
    hmconfig.webservice_url = webservice_url
    client = harvestmedia.api.client.Client()
    libraries = Library.get_libraries()
