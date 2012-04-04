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
from utils import get_random_md5

api_key = '12345'


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_libraries(HTTPMock):
    client = init_client()
    http = HTTPMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = get_random_md5()
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

    libraries = Library.query.get_libraries(client)
    assert isinstance(libraries, list)

    library = libraries[0]
    assert library.id == 'abc123'
    assert library.name == 'VIDEOHELPER'


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_library_albums(HTTPMock):
    client = init_client()
    http = HTTPMock()
    expiry = datetime.datetime.today().isoformat()
    test_token = get_random_md5()
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

    libraries = Library.query.get_libraries(client)
    assert isinstance(libraries, list)

    test_album_id = get_random_md5()
    mock_response = StringIO.StringIO(textwrap.dedent("""<responsealbums>
                                        <albums>
                                        <album libraryid="abc123" featured="false" code="HM001" detail="Razor-sharp pop&amp; rock
                                        bristling with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                        name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%(test_album_id)s"/>
                                        <album libraryid="19b8f5935503adde" featured="false" code="HM002" detail=" Contemporary beats
                                        fused with orchestral elements." name="HM 002 Sample Album " displaytitle="HM 002 Sample Album "
                                        id="67a6aed83a741a06"/>
                                        </albums>
                                        </responsealbums>""") % {'test_album_id': test_album_id})

    mock_response.status = 200
    http.getresponse.return_value = mock_response
    library = libraries[0]
    albums = library.get_albums()
    assert isinstance(albums, list)
    assert albums[0].id == test_album_id
