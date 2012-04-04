# -*- coding: utf-8 -*-
import datetime
import hashlib
import logging
import mock
from nose.tools import raises
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.library import Library

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
@raises(harvestmedia.api.exceptions.InvalidAPIResponse)
def test_xml_failure(HttpMock):
    api_key = get_random_md5()
    content = '<xml><this xml is malformed</xml>'
    http = build_http_mock(HttpMock, content=content)
    client = harvestmedia.api.client.Client(api_key=api_key, debug_level='DEBUG')
    client.get_service_info()


@mock.patch('harvestmedia.api.client.httplib2.Http')
@raises(harvestmedia.api.exceptions.InvalidAPIResponse)
def test_non_200(HttpMock):
    api_key = get_random_md5()
    content = '<xml><this xml is malformed</xml>'
    http = build_http_mock(HttpMock, response_status=400, content=content)
    client = harvestmedia.api.client.Client(api_key=api_key, debug_level='DEBUG')
    client.get_service_info()


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_service_token(HttpMock):
    api_key = get_random_md5()
    expiry = datetime.datetime.now()
    expiry += datetime.timedelta(hours=22) # offset for HM timezone
    test_token = hashlib.md5(str(expiry)).hexdigest() # generate an md5 from the date for testing

    return_values = [
         (200, """<?xml version="1.0" encoding="utf-8"?>
                    <responseservicetoken>
                        <token value="%s" expiry="%s"/>
                    </responseservicetoken>""" % \
                    (test_token, expiry.strftime("%Y-%m-%dT%H:%M:%S"))),

         (200, """<?xml version="1.0" encoding="utf-8"?>
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
                    </responseserviceinfo>"""),
    ]
                        
    http = build_http_mock(HttpMock, responses=return_values)                        
    client = harvestmedia.api.client.Client(api_key=api_key, debug_level='DEBUG')

    # get the debug level to cover the getter
    print client.debug_level
    
    assert client.config.service_token.token == test_token
    assert client.config.service_token.expiry == expiry.strftime("%Y-%m-%dT%H:%M:%S")


@mock.patch('harvestmedia.api.client.httplib2.Http')
@raises(harvestmedia.api.exceptions.InvalidToken)
def test_invalid_token(HttpMock):
    api_key = get_random_md5()
    content = """<?xml version="1.0" encoding="utf-8"?>
                    <memberaccount>
                        <error>
                            <code>5</code>
                            <description>Invalid Token</description>
                        </error>
                    </memberaccount>"""

    http = build_http_mock(HttpMock, content=content)
    client = harvestmedia.api.client.Client(api_key=api_key)
    libraries = Library.get_libraries(client)


@mock.patch('harvestmedia.api.client.httplib2.Http')
@raises(harvestmedia.api.exceptions.CorruptInputData)
def test_corrupt_input_data(HttpMock):
    api_key = get_random_md5()
    content = """<?xml version="1.0" encoding="utf-8"?>
                    <memberaccount>
                        <error>
                            <code>1</code>
                            <description>Corrupt Input Data</description>
                        </error>
                    </memberaccount>"""
    http = build_http_mock(HttpMock, content=content)
    client = harvestmedia.api.client.Client(api_key=api_key)
    libraries = Library.get_libraries(client)


@mock.patch('harvestmedia.api.client.httplib2.Http')
@raises(harvestmedia.api.exceptions.IncorrectInputData)
def test_invalid_input_data(HttpMock):
    api_key = get_random_md5()
    content = """<?xml version="1.0" encoding="utf-8"?>
                    <memberaccount>
                        <error>
                            <code>2</code>
                            <description>Incorrect Input Data</description>
                        </error>
                    </memberaccount>"""
    http = build_http_mock(HttpMock, content=content)
    client = harvestmedia.api.client.Client(api_key=api_key)
    libraries = Library.get_libraries(client)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_expired_token_refetch(HttpMock):
    api_key = get_random_md5()
    expiry = datetime.datetime.now()
    expiry2 = expiry + datetime.timedelta(hours=22)
    test_second_token = get_random_md5()

    return_values = [
                     (200, """<?xml version="1.0" encoding="utf-8"?>
                                <responseservicetoken>
                                    <token value="%s" expiry="%s"/>
                                </responseservicetoken>""" % \
                                (test_second_token, expiry2.strftime("%Y-%m-%dT%H:%M:%S"))),
                     (200, """<?xml version="1.0" encoding="utf-8"?>
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
                                </responseserviceinfo>"""),
                    ]
                        
    client = init_client()

    # force-expire the token
    client.config.service_token.expiry = (datetime.datetime.now() - datetime.timedelta(hours=12)).isoformat()

    http = build_http_mock(HttpMock, responses=return_values)
    # this should fetch a new token since the old one is expired
    client.get_service_info()

    # token should match the SECOND token
    assert client.config.service_token.token == test_second_token
