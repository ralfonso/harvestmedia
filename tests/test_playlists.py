# -*- coding: utf-8 -*-
import datetime
import hashlib
from nose.tools import raises, with_setup
import mock
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.member import Member
from harvestmedia.api.playlist import Playlist

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_add_playlist(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    content = """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(id)s" name="%(name)s" />
                    </playlists>
                </ResponsePlaylists>""" % \
                    {'id': test_playlist_id,
                     'name': test_playlist_name}

    http = build_http_mock(HttpMock, content=content)
    playlist = Playlist.add(_client=client, member_id=test_member_id, playlist_name=test_playlist_name)

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_member_playlists(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    member_xml = ET.fromstring("""<memberaccount id="%(test_member_id)s">
                                    <username>%(username)s</username>
                                    <firstname>%(firstname)s</firstname>
                                    <lastname>%(lastname)s</lastname>
                                    <email>%(email)s</email>
                                </memberaccount>""" % {'test_member_id': test_member_id,
                                                       'username': username,
                                                       'firstname': firstname,
                                                       'lastname': lastname,
                                                       'email': email})

    member = Member._from_xml(member_xml, client)

    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    content = """<?xml version="1.0" encoding="utf-8"?>
                     <ResponsePlaylists>
                        <playlists>
                            <playlist id="%(id)s" name="%(name)s">
                                <tracks>
                                    <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure
                                        you’re down the front for this fiery Post Punk workout."
                                        composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                        name="Guerilla Pop" id="17376d36f309f18d" keywords="" lyrics=""
                                        displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                        bpm="" mixout="" frequency="44100" bitrate="1411" />
                                </tracks>
                            </playlist>
                        </playlists>
                    </ResponsePlaylists>""" % {'id': test_playlist_id,
                                            'name': test_playlist_name}

    http = build_http_mock(HttpMock, content=content)
    playlists = member.get_playlists()

    assert isinstance(playlists, list)

    playlist = playlists[0]

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_featured_playlists(HttpMock):
    client = init_client()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    content = """<?xml version="1.0" encoding="utf-8"?>
                     <responsefeaturedplaylists>
                        <playlists>
                            <playlist id="%(id)s" name="%(name)s">
                                 <tracks>
                                    <track tracknumber="001" time="01:07" lengthseconds="67" comment="If a certain
                                    animated film studio were to remake The Andy Griffith Show as a digital short, we'd
                                    nominate this for the theme. Warm, chunky, a little slow on the uptake... a.k.a. the
                                    anti-lemonade song. Ending starts @ 1:08. Lite Mix, without main rhythm acoustic
                                    guitars." composer="D. Holter/K. White" publisher="TLL UNDERscore Nashcap (ASCAP)"
                                    name="Pencilneck Strut" id="902dea1d377473df" keywords="Cute, Goofy, Lighthearted,
                                    Happy, Comical, Twang, Rural, Fun, Mischievous, Celebration, Campy, Childlike,
                                    Cheerful, Simple, Quirky, Swampy, Playful" lyrics="" displaytitle="Pencilneck Strut"
                                    genre="Country" tempo="Medium" instrumentation="Acoustic Guitar, Banjo, Percussion"
                                    bpm="130" mixout="Alt2" frequency="2650" bitrate="24" />
                                </tracks>
                            </playlist>
                        </playlists>
                    </responsefeaturedplaylists>
              """ % {'id': test_playlist_id,
                     'name': test_playlist_name}

    http = build_http_mock(HttpMock, content=content)
    playlists = Playlist.query.get_featured_playlists(client)

    assert isinstance(playlists, list)

    playlist = playlists[0]

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_add_playlist_client_missing():
    playlist = Playlist.add()


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_add_playlist_member_id_missing():
    client = init_client()
    playlist = Playlist.add(_client=client)


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_add_playlist_name_missing():
    client = init_client()
    test_member_id = 123
    playlist = Playlist.add(_client=client, member_id=test_member_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_add_track(HttpMock):
    client = init_client()
    test_playlist_id = get_random_md5()
    track_id = get_random_md5()

    content = """<?xml version="1.0" encoding="utf-8"?>
                    <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                        <code>OK</code>
                    </responsecode>"""

    http = build_http_mock(HttpMock, content=content)
    playlist = Playlist(_client=client)
    playlist.member_id = 123
    playlist.id = test_playlist_id
    playlist.add_track(track_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    test_track_id = get_random_md5()

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                            <tracks>
                                <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure you’re
                                down the front for this fiery Post Punk workout."
                                composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                name="Guerilla Pop" id="%(test_track_id)s" keywords=""
                                lyrics="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                            </tracks>
                        </playlist>
                    </playlists>
                </ResponsePlaylists>""" % locals()),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <code>OK</code>
                 </responsecode>""",),
    ]

    http = build_http_mock(HttpMock, responses=return_values)
    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlists[0].remove()


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove_track(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'

    now = datetime.datetime.today().isoformat()
    test_member_id = get_random_md5()
    now = datetime.datetime.today().isoformat()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    track_id = '17376d36f309f18d'

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                     <ResponsePlaylists>
                        <playlists>
                            <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                                <tracks>
                                    <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make
                                    sure you’re down the front for this fiery Post Punk workout."
                                    composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                    name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics=""
                                    displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                    instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                                </tracks>
                            </playlist>
                        </playlists>
                    </ResponsePlaylists>""" % locals(),),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <code>OK</code>
                </responsecode>"""),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlists[0].remove_track(track_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_playlist_update(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    test_playlist_update_name = 'test playlist update'
    track_id = '17376d36f309f18d'

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                            <tracks>
                                <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make
                                sure you’re down the front for this fiery Post Punk workout."
                                composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics=""
                                displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                            </tracks>
                        </playlist>
                    </playlists>
                </ResponsePlaylists>""" % locals()),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                     <code>OK</code>
                 </responsecode>"""),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlist = playlists[0]

    playlist.name = test_playlist_update_name
    playlist.update()
    assert playlist.name == test_playlist_update_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_download_url(HttpMock):
    client = init_client()
    member_id = 'bacba2b288328238bcbac'
    track_format = 'mp3'
    playlist_id = "908098a8a0ba8b065"
    playlist_xml = ET.fromstring("""
                <playlist id="%(playlist_id)s" name="sample playlist">
                    <tracks>
                        <track tracknumber="1" time="02:50" lengthseconds="170"
                            comment="Track Comment" composer="JJ Jayjay"
                            publisher="PP Peepee" name="Epic Track" albumid="1abcbacbac33" id="11bacbcbabcb3b2823"
                            displaytitle="Epic Track" genre="Pop / Rock"
                            bpm="100" mixout="FULL" frequency="44100" bitrate="1411"
                            dateingested="2008-05-15 06:08:18"/>
                    </tracks>
                </playlist>""" % locals())

    playlist = Playlist._from_xml(playlist_xml, client)

    download_url = playlist.get_download_url(track_format, member_id)
    download_url_template = client.config.playlistdownload_url

    format_identifier = client.config.get_format_identifier(track_format)
    expected_url = download_url_template.replace('{memberaccountid}', member_id).\
                                         replace('{id}', playlist_id).\
                                         replace('{trackformat}', format_identifier)
    assert download_url == expected_url, 'url: %s != expected: %s' % (download_url, expected_url)


@raises(harvestmedia.api.exceptions.MissingParameter)
@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_download_url_missing_format(HttpMock):
    client = init_client()
    member_id = 'bacba2b288328238bcbac'
    track_format = 'BAD-FORMAT'
    playlist_id = "908098a8a0ba8b065"
    playlist_xml = ET.fromstring("""
                <playlist id="%(playlist_id)s" name="sample playlist">
                    <tracks>
                        <track tracknumber="1" time="02:50" lengthseconds="170"
                            comment="Track Comment" composer="JJ Jayjay"
                            publisher="PP Peepee" name="Epic Track" albumid="1abcbacbac33" id="11bacbcbabcb3b2823"
                            displaytitle="Epic Track" genre="Pop / Rock"
                            bpm="100" mixout="FULL" frequency="44100" bitrate="1411"
                            dateingested="2008-05-15 06:08:18"/>
                    </tracks>
                </playlist>""" % locals())

    playlist = Playlist._from_xml(playlist_xml, client)
    download_url = playlist.get_download_url(track_format, member_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_playlist_art_url(HttpMock):
    client = init_client()

    playlist_id = '112358'
    playlist_xml = ET.fromstring(textwrap.dedent("""<playlist name="EFF!" id="%s" 
                                                    createddate="2012-04-17 06:24:45"
                                                    trackcount="0" />""" % (playlist_id)))
    playlist_art_url = 'http://download.harvestmedia.net/wsplaylistart/8185d768cd8fcaa7/{id}/{width}/{height}'

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
                        waveform="http://asset.harvestmedia.net/waveform/8185d768cd8fcaa7/{id}/{width}/{height}"
                        trackstream="http://asset.harvestmedia.net/trackstream/8185d768cd8fcaa7/{id}"
                        trackdownload=" http://asset.harvestmedia.net/trackdownload/8185d768cd8fcaa7/{id}/{trackformat}"
                        playlistart="%(playlist_art_url)s" />
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

    playlist = Playlist._from_xml(playlist_xml, client)
    cover_art_url = playlist.get_cover_url(width, height)

    expected_url = playlist_art_url.replace('{id}', playlist_id).replace('{width}', str(width)).replace('{height}', str(height))
    assert cover_art_url == expected_url
