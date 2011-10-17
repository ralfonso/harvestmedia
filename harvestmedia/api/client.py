# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import httplib

import exceptions
import config
import logging
import iso8601
import pytz
from signals import signals
import datetime

logger = logging.getLogger('harvestmedia')

class Client(object):
    """

    """

    
    def _set(self, param, default=None, **kwargs):
        if kwargs.get(param, None):
            setattr(self, param, kwargs[param])
        elif hasattr(self.config, param):
            setattr(self, param, getattr(self.config, param))
        elif default:
            setattr(self, param, default)

    def __init__(self, **kwargs):
        """
        initialize the Client object

        api_key: the Harvest Media API key to use
        webservice_url: the base Harvest Media API URL
        """

        self.config = config.Config()

        self._set('api_key', **kwargs)
        self._set('webservice_url', **kwargs)
        self._set('service_token', **kwargs)
        self._set('album_art_url', **kwargs)
        self._set('debug', **kwargs)

        def handle_expired_token():
            self.request_service_token()

        signals.add_signal('expired-token')
        signals.connect('expired-token', handle_expired_token)

        if not self.config.service_token:
            if self.debug:
                logger.debug('requesting service token')
            self.request_service_token()

        if not self.config.album_art_url:
            self.get_service_info()

    def __add_service_token(self, uri):
        if '{{service_token}}' not in uri:
            return uri

        try:
            service_token = self.config.service_token.token
        except exceptions.TokenExpired:
            self.request_service_token()
            service_token = self.config.service_token.token

        uri = uri.replace('{{service_token}}', service_token)

        return uri

    def _handle_response(self, response):
        xml_doc_str = response.read()

        if response.status != 200:
            response_status = response.status
            response_body = response.read()

            if self.debug:
                logger.debug('HTTP: non 200 status received from server: ' + str(response_status))

            exc = exceptions.InvalidAPIResponse('non 200 HTTP error returned from server: ' + str(response_status) + ': ' + str(response_body))
            exc.code = response.status
            raise exc

        if self.debug:
            logger.debug("server response: " + xml_doc_str.decode('utf-8'))

        try:
            root = ET.fromstring(xml_doc_str)
        except ET.ParseError, e:
            raise exceptions.InvalidAPIResponse, "Unable to read the XML from the API server: " + e.message


        error = root.find('error')
        if error is not None:
            code = error.find('code')
            if code is not None:
                if code.text == '1':
                    raise exceptions.CorruptInputData()
                elif code.text == '2':
                    description = error.find('description')
                    reason = description.text if description is not None else 'Incorrect Input Data'
                    raise exceptions.IncorrectInputData(reason)
                elif code.text == '5':
                    signals.send('expired-token')
                    raise exceptions.InvalidToken()
                elif code.text == '7':
                    raise exceptions.MemberDoesNotExist()

        return root



    def get_xml(self, method_uri):
        method_uri = self.config.webservice_prefix + self.__add_service_token(method_uri)
        if self.config.webservice_url_parsed.scheme == 'http':
            http = httplib.HTTPConnection(self.config.webservice_host)
        elif self.config.webservice_url_parsed.scheme == 'https':
            http = httplib.HTTPSConnection(self.config.webservice_host)
        http.request('GET', method_uri)

        if self.debug:
            logger.debug("url: %s://%s%s" % (self.config.webservice_url_parsed.scheme, self.config.webservice_host, method_uri))

        response = http.getresponse()

        return self._handle_response(response)

    def post_xml(self, method_uri, xml_post_body):
        method_url = self.config.webservice_url + self.__add_service_token(method_uri)

        if self.config.webservice_url_parsed.scheme == 'http':
            http = httplib.HTTPConnection(self.config.webservice_host)
        elif self.config.webservice_url_parsed.scheme == 'https':
            http = httplib.HTTPSConnection(self.config.webservice_host)

        if self.debug:
            logger.debug("url: " + method_url)
            logger.debug("posting XML: " + xml_post_body)

        http.request('POST', method_url, xml_post_body, {'Content-Type': 'application/xml'}) 

        response = http.getresponse()
        return self._handle_response(response)

    def request_service_token(self):
        method_uri = '/getservicetoken/' + self.api_key

        root = self.get_xml(method_uri)
        xml_token = root.find('token')
        if self.debug:
            logger.debug('got token: %s' % xml_token.get('value'))
        token = xml_token.get('value')
        expiry = xml_token.get('expiry')

        self.config.service_token = config.ServiceToken(self.config, token, expiry)


    def get_service_info(self):
        method_uri = '/getserviceinfo/{{service_token}}'

        root = self.get_xml(method_uri)
        asset_url = root.find('asseturl')
        self.config.album_art_url = asset_url.get('albumart')
        self.config.waveform_url = asset_url.get('waveform')
        self.config.download_url = asset_url.get('trackdownload')
        self.config.playlistdownload_url = asset_url.get('playlistdownload')
        self.config.stream_url = asset_url.get('trackstream')

        self.config.trackformats = []
        
        trackformats_xml = root.find('trackformats')

        if trackformats_xml:
            for trackformat_xml in trackformats_xml.getchildren():
                self.config.trackformats.append(dict(trackformat_xml.items()))     


class APIClient(Client):
    def __init__(self, api_key=None, webservice_url=None):
        super(APIClient, self).__init__(api_key=api_key, webservice_url=webservice_url)
        if not self.api_key:
            raise exceptions.NotConfiguredError("Please specify an api_key")

        if not self.webservice_url:
            raise exceptions.NotConfiguredError("Please specify the webservice_url")
