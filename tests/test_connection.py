# -*- coding: utf-8 -*-
import datetime
import hashlib
import mock
from nose.tools import raises
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.library import Library

from setup import init_client

api_key = '12345'


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
@raises(harvestmedia.api.exceptions.InvalidAPIResponse)
def test_xml_failure(HTTPMock):
    http = HTTPMock()
    mock_response = StringIO.StringIO('<xml><this xml is malformed</xml>')
    mock_response.status = 200
    http.getresponse.return_value = mock_response
    client = harvestmedia.api.client.Client(api_key=api_key)
    client.get_service_info()


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_service_token(HTTPMock):
    expiry = datetime.datetime.now()
    expiry += datetime.timedelta(hours=22) # offset for HM timezone
    test_token = hashlib.md5(str(expiry)).hexdigest() # generate an md5 from the date for testing

    return_values = [
                     '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry.strftime("%Y-%m-%dT%H:%M:%S")),
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
    client = harvestmedia.api.client.Client(api_key=api_key)
    
    assert client.config.service_token.token == test_token
    assert client.config.service_token.expiry == expiry.strftime("%Y-%m-%dT%H:%M:%S")


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_libraries(HTTPMock):
    client = init_client()
    http = HTTPMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = hashlib.md5(expiry).hexdigest() # generate an md5 from the date for testing
    http.getresponse.return_value = StringIO.StringIO('<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry))
    
    mock_response = StringIO.StringIO("""
        <ResponseLibraries>
            <libraries> 
                <library id="abc123" name="VIDEOHELPER" detail="Library description" />
                <library id="abc125" name="MODULES" detail="Library description" />
            </libraries>
        </ResponseLibraries>""")
    mock_response.status = 200
    http.getresponse.return_value = mock_response

    libraries = Library.get_libraries(client)
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
    client = harvestmedia.api.client.Client(api_key=api_key)
    libraries = Library.get_libraries(client)


@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_expired_token(HTTPMock):
    http = HTTPMock()
    expiry = datetime.datetime.now()
    expiry2 = expiry + datetime.timedelta(hours=22)
    test_token = hashlib.md5(str(expiry)).hexdigest() # generate an md5 from the date for testing
    return_values = [
                     '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry.strftime("%Y-%m-%dT%H:%M:%S")),
                     '<?xml version="1.0" encoding="utf-8"?><responseservicetoken><token value="%s" expiry="%s"/></responseservicetoken>' % (test_token, expiry2.strftime("%Y-%m-%dT%H:%M:%S")),
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

    http.getresponse.side_effect = side_effect
    
    client = init_client()
    client.config.service_token.expiry = (datetime.datetime.now() - datetime.timedelta(hours=12)).isoformat()
    try:
        client.get_service_info()
    except Exception, e:
        assert isinstance(e, harvestmedia.api.exceptions.TokenExpired)

    client.get_service_info()
    assert client.config.service_token.expiry == expiry2.strftime("%Y-%m-%dT%H:%M:%S")
