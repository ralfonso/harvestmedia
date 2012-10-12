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

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_libraries(HttpMock):
    client = init_client()

    return_values = [
         (200, """<ResponseLibraries>
                    <libraries>
                        <library id="abc123" name="VIDEOHELPER" detail="Library description" />
                        <library id="abc125" name="MODULES" detail="Library description" />
                    </libraries>
                </ResponseLibraries>"""),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    libraries = Library.query.get_libraries(client)
    assert isinstance(libraries, list)

    library = libraries[0]
    assert library.id == 'abc123'
    assert library.name == 'VIDEOHELPER'


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_library_albums(HttpMock):
    client = init_client()
    test_album_id = get_random_md5()

    return_values = [
         (200, """<ResponseLibraries>
                    <libraries>
                        <library id="abc123" name="VIDEOHELPER" detail="Library description" />
                        <library id="abc125" name="MODULES" detail="Library description" />
                    </libraries>
                </ResponseLibraries>"""),

         (200, """<responsealbums>
                    <albums>
                        <album libraryid="abc123" featured="false" code="HM001" detail="Razor-sharp pop&amp; rock
                        bristling with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                        name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%(test_album_id)s"/>
                        <album libraryid="19b8f5935503adde" featured="false" code="HM002" detail=" Contemporary beats
                        fused with orchestral elements." name="HM 002 Sample Album " displaytitle="HM 002 Sample Album "
                        id="67a6aed83a741a06"/>
                        </albums>
                    </responsealbums>""" % {'test_album_id': test_album_id}),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    libraries = Library.query.get_libraries(client)
    assert isinstance(libraries, list)

    library = libraries[0]
    albums = library.get_albums()
    assert isinstance(albums, list)
    assert albums[0].id == test_album_id

@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_library_logo_url(HttpMock):
    client = init_client()

    width = 200
    height = 400

    library_id = '11235813'
    library_logo_url = "http://download.harvestmedia.net/wslibrarylogo/8185d768cd8fcaa7/{id}/{width}/{height}"

    library_xml = ET.fromstring(textwrap.dedent("""<library detail="" name="" id="%(library_id)s" location="Talent, Oregon"
                      website="http://risefromyourgrave.com" librarylogourl="%(library_logo_url)s" />""" % locals()))

    library = Library._from_xml(library_xml, client)
    library_logo_url = library.get_logo_url(width, height)

    expected_url = library_logo_url.replace('{id}', library_id).replace('{width}', str(width)).replace('{height}]', str(height))
    assert library_logo_url == expected_url
