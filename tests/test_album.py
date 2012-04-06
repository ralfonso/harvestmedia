# -*- coding: utf-8 -*-
import datetime
import mock
import StringIO
import textwrap
import xml.etree.cElementTree as ET

from harvestmedia.api.album import Album

from utils import build_http_mock, get_random_md5, init_client


def test_album_init():
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))

    album = Album.from_xml(album_xml, client)
    assert album.id == album_id


def test_album_dict():
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))

    album = Album.from_xml(album_xml, client)
    album_dict = album.as_dict()
    assert album_dict['id'] == album_id


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_album_tracks(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))

    return_values = [
        (200, """<responsetracks>
                    <tracks>
                        <track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for
                               this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher=""
                               name="Guerilla Pop" albumid="%(album_id)s" id="17376d36f309f18d" keywords=""
                               displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout=""
                               frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>
                        <track tracknumber="2" time="02:46" lengthseconds="166" comment="Poignant electric guitars. Brooding
                        acoustic strums." composer="&quot;S. Milton, J. Wygens&quot;" publisher="" name="Hat And Feather"
                        albumid="%(album_id)s" id="635f90a4db673855" keywords="" displaytitle="Hat And Feather"
                        genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411"
                        dateingested="2008-05-15 06:08:18"/>
                    </tracks>
                </responsetracks>""" % locals()),
    ]

    http = build_http_mock(HttpMock, responses=return_values)
    album = Album.from_xml(album_xml, client)
    tracks = album.get_tracks(get_full_detail=False)
    assert tracks[0].albumid == album_id


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_album_notracks(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))

    return_values = [
        (200, """<responsetracks>
                    <tracks>
                    </tracks>
                </responsetracks>""" % locals(),),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    album = Album.from_xml(album_xml, client)
    tracks = album.get_tracks(get_full_detail=False)
    assert len(tracks) == 0


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_album_tracks_fulldetail(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))

    return_values = [
        (200, """<responsetracks>
                    <tracks>
                        <track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for
                               this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher=""
                               name="Guerilla Pop" albumid="%(album_id)s" id="17376d36f309f18d" keywords=""
                               displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout=""
                               frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>
                        <track tracknumber="2" time="02:46" lengthseconds="166" comment="Poignant electric guitars. Brooding
                        acoustic strums." composer="&quot;S. Milton, J. Wygens&quot;" publisher="" name="Hat And Feather"
                        albumid="%(album_id)s" id="635f90a4db673855" keywords="" displaytitle="Hat And Feather"
                        genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411"
                        dateingested="2008-05-15 06:08:18"/>
                    </tracks>
                </responsetracks>""" % locals(),),
        (200, """<responsetracks>
                    <tracks>
                        <track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for
                               this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher=""
                               name="Guerilla Pop" albumid="%(album_id)s" id="17376d36f309f18d" keywords=""
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
                        <track tracknumber="2" time="02:46" lengthseconds="166" comment="Poignant electric guitars. Brooding
                        acoustic strums." composer="&quot;S. Milton, J. Wygens&quot;" publisher="" name="Hat And Feather"
                        albumid="%(album_id)s" id="635f90a4db673855" keywords="" displaytitle="Hat And Feather"
                        genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411"
                        dateingested="2008-05-15 06:08:18"/>
                    </tracks>
                </responsetracks>""" % locals(),),
    ]

    http = build_http_mock(HttpMock, responses=return_values)
    album = Album.from_xml(album_xml, client)
    tracks = album.get_tracks()
    assert tracks[0].albumid == album_id


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_cover_url(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'
    album_xml = ET.fromstring(textwrap.dedent("""<album featured="false" code="HM001" detail="Razor-sharp pop&amp; rock bristling
                                                    with spiky guitars &amp; infectious, feelgood inspiration … and tons of attitude."
                                                    name="HM 001 Sample Album" displaytitle="HM 001 Sample Album " id="%s"/> """ % (album_id)))
    album_art_url = "http://asset.harvestmedia.net/albumart/8185d768cd8fcaa7/{id}/{width}/{height}"
    expiry = datetime.datetime.now()
    test_token = get_random_md5()

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                    <responseservicetoken>
                        <token value="%s" expiry="%s"/>
                    </responseservicetoken>""" % \
                    (test_token, expiry.strftime("%Y-%m-%dT%H:%M:%S"))),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                <responseserviceinfo>
                    <asseturl
                        albumart="%(album_art_url)s"
                        waveform="http://asset.harvestmedia.net/waveform/8185d768cd8fcaa7/{id}/{width}/{height}"
                        trackstream="http://asset.harvestmedia.net/trackstream/8185d768cd8fcaa7/{id}"
                        trackdownload=" http://asset.harvestmedia.net/trackdownload/8185d768cd8fcaa7/{id}/{trackformat}" />
                    <trackformats>
                      <trackformat identifier="8185d768cd8fcaa7" extension="mp3" bitrate="320" samplerate="48" samplesize="16" />
                      <trackformat identifier="768cd8fcaa8185d7" extension="wav" bitrate="1536" samplerate="48" samplesize="16" />
                      <trackformat identifier="7jsi8fcaa818df57" extension="aif" bitrate="1536" samplerate="48" samplesize="16" />
                    </trackformats>
                </responseserviceinfo>""" % locals()),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    width = 200
    height = 300

    album = Album.from_xml(album_xml, client)
    cover_art_url = album.get_cover_url(width, height)

    expected_url = album_art_url.replace('{id}', album_id).replace('{width}', str(width)).replace('{height}', str(height))
    assert cover_art_url == expected_url
