# -*- coding: utf-8 -*-
import StringIO

import mock
import datetime, hashlib
from datetime import timedelta

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

@mock.patch('harvestmedia.api.client.httplib2.Http')
def init_client(HTTPMock):
    expiry = datetime.datetime.now()
    expiry += timedelta(hours=22) # offset for HM timezone
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
    client = harvestmedia.api.client.Client(api_key=api_key, debug_level='DEBUG')
    return client
