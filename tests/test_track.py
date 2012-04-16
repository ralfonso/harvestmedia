# -*- coding: utf-8 -*-
import datetime
import hashlib
import mock
from nose.tools import raises
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.track import Track

from utils import build_http_mock, get_random_md5, init_client


def test_track_dict():
    client = init_client()
    track_id = '17376d36f309f18d'
    track_xml = ET.fromstring(textwrap.dedent("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down
                                                  the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;"
                                                  publisher="" name="Guerilla Pop" albumid="1c5f47572d9152f3" id="%(track_id)s"
                                                  keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                                  bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""") % locals())

    track = Track._from_xml(track_xml, client)
    track_dict = track.as_dict()
    assert track_dict['id'] == track_id


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_tracks_get_by_id(HttpMock):
    client = init_client()
    track_id = '17376d36f309f18d'
    track_name = 'Guerilla Pop'
    track_xml = ET.fromstring(textwrap.dedent("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down
                                                  the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;"
                                                  publisher="" name="%(track_name)s" albumid="1c5f47572d9152f3" id="%(track_id)s"
                                                  keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                                  bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""") % locals())

    return_values = [
        (200, """<responsetracks>
                <tracks>
                <track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front
                for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher=""
                name="%(track_name)s" albumid="1111001010001aaabeb" id="17376d36f309f18d" keywords=""
                displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout=""
                frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18">
                    <categories>
                      <category name="Tuning" id="07615de0da9a3d50">
                        <attributes>
                          <attribute name="Energy" id="a7cc2fe1b4075e51">
                            <attributes>
                              <attribute name="4" In="" Motion=""
                              id="97fda140bf94f8ca" />
                            </attributes>
                          </attribute>
                          <attribute name="Genetics" id="a5306d79fa80d3da">
                            <attributes>
                              <attribute name="3" Blended="" id="387b65044f597b48" />
                            </attributes>
                          </attribute>
                          <attribute name="Mood" id="05c1d9f5bb63b113">
                            <attributes>
                              <attribute name="1" id="527d6c887023f4ee" />
                            </attributes>
                          </attribute>
                          <attribute name="Tempo" id="65ea5898a4549788">
                            <attributes>
                              <attribute name="3" Medium="" id="b7f9cd0ca260b61a" />
                            </attributes>
                          </attribute>
                          <attribute name="Tone" id="22aadd9f2935aabe">
                            <attributes>
                              <attribute name="2" Leaning="" Dark=""
                              id="aa9c33fef3c5756f" />
                            </attributes>
                          </attribute>
                          <attribute name="Vocals" id="ea584a3d9b4fb116">
                            <attributes>
                              <attribute name="0" id="da2362b0e30b131f" />
                            </attributes>
                          </attribute>
                        </attributes>
                      </category>
                      <category name="Instrumentation" id="7907138b683424f4">
                        <attributes>
                          <attribute name="Guitars" id="abf2d935cb4182b7">
                            <attributes>
                              <attribute name="Electric" Distorted=""
                              id="96d809f485c198d4" />
                            </attributes>
                          </attribute>
                          <attribute name="Bass" id="080a1841ed350bbb">
                            <attributes>
                              <attribute name="Electric" id="a4fc0c1d3ad2cd64" />
                            </attributes>
                          </attribute>
                          <attribute name="Drums" id="16fd25d513dce9dd">
                            <attributes>
                              <attribute name="Live" id="35babb65b41e2028" />
                            </attributes>
                          </attribute>
                          <attribute name="Percussion" id="aa2850c4d1579d12">
                            <attributes>
                              <attribute name="Electronic" id="29aefdd818757ea3" />
                            </attributes>
                          </attribute>
                          <attribute name="Keyboards" id="660d379e9f7a6faf">
                            <attributes>
                              <attribute name="Synth" id="61454b4396a1f362" />
                            </attributes>
                          </attribute>
                        </attributes>
                      </category>
                    </categories>
                </track>
            </tracks>
        </responsetracks>""" % locals(),),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    track = Track.query.get_by_id(track_id, client)

    assert track.id == track_id
    assert track.name == track_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_waveform_url(HttpMock):
    client = init_client()
    track_id = '17376d36f309f18d'
    track_name = 'Guerilla Pop'
    track_xml = ET.fromstring(textwrap.dedent("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down
                                                  the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;"
                                                  publisher="" name="%(track_name)s" albumid="1c5f47572d9152f3" id="%(track_id)s"
                                                  keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                                  bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""") % locals())

    track = Track._from_xml(track_xml, client)

    width = 200
    height = 300
    waveform_url = track.get_waveform_url(width, height)

    waveform_url_template = client.config.waveform_url
    expected_url = waveform_url_template.replace('{id}', track_id).replace('{width}', str(width)).replace('{height}', str(height))
    assert waveform_url == expected_url


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_download_url(HttpMock):
    client = init_client()
    member_id = 'bacba2b288328238bcbac'
    track_format = 'mp3'
    track_id = '17376d36f309f18d'
    track_name = 'Guerilla Pop'
    track_xml = ET.fromstring(textwrap.dedent("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down
                                                  the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;"
                                                  publisher="" name="%(track_name)s" albumid="1c5f47572d9152f3" id="%(track_id)s"
                                                  keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                                  bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""") % locals())

    track = Track._from_xml(track_xml, client)

    download_url = track.get_download_url(track_format, member_id)
    download_url_template = client.config.download_url

    format_identifier = client.config.get_format_identifier(track_format)
    expected_url = download_url_template.replace('{memberaccountid}', member_id).\
                                         replace('{id}', track_id).\
                                         replace('{trackformat}', format_identifier)
    assert download_url == expected_url, 'url: %s != expected: %s' % (download_url, expected_url)


@raises(harvestmedia.api.exceptions.MissingParameter)
@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_download_url_missing_format(HttpMock):
    client = init_client()
    member_id = 'bacba2b288328238bcbac'
    track_format = 'BAD-FORMAT'
    track_id = '17376d36f309f18d'
    track_name = 'Guerilla Pop'
    track_xml = ET.fromstring(textwrap.dedent("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down
                                                  the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;"
                                                  publisher="" name="%(track_name)s" albumid="1c5f47572d9152f3" id="%(track_id)s"
                                                  keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                                  bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""") % locals())

    track = Track._from_xml(track_xml, client)

    download_url = track.get_download_url(track_format, member_id)
