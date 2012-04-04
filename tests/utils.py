import datetime
import hashlib
import mock
import random

from harvestmedia.api.client import Client

def get_random_md5():
    return '%032x' % (random.getrandbits(128))


def build_request_rv(response_or_status, content):
    try:
        status = int(response_or_status)
        response = mock.Mock()
        response.status = status
    except ValueError:
        response = response_or_status

    return (response, content)        


def build_http_mock(http_mock, response_status=200, response=None, content=None, responses=None):
    """Create a mock of the httplib2.Http class that can return 
    one or more responses

    """

    http = http_mock()

    if responses:
        def side_effect(*args):
            response = responses.pop(0)
            return build_request_rv(response[0], response[1])
        
        http.request.side_effect = side_effect

    else:
        if response:
            mock_response = response
        else:
            mock_response = mock.Mock()
            mock_response.status = response_status

        print 'MOCK CONTENT %s' % str(content)
        mock_return = (mock_response, content)            
        http.request.return_value = mock_return

    return http            


@mock.patch('harvestmedia.api.client.httplib2.Http')
def init_client(HttpMock):
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
    api_key = '1234567'
    client = Client(api_key=api_key, debug_level='DEBUG')
    return client
