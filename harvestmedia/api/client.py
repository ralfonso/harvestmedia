# -*- coding: utf-8 -*-
import datetime
import logging
import httplib
import iso8601
import pytz
import xml.etree.cElementTree as ET

import exceptions
from config import Config, ServiceToken
from signals import signals


logger = logging.getLogger('harvestmedia')


class Client(object):

    def _set(self, param, default=None, **kwargs):
        if kwargs.get(param, None):
            setattr(self, param, kwargs[param])
        else:
            setattr(self, param, default)

    def __init__(self, **kwargs):
        """
        initialize the Client object

        api_key: the Harvest Media API key to use
        webservice_url: the base Harvest Media API URL
        """

        self._set('api_key', **kwargs)
        self._set('debug_level', 'DEBUG', **kwargs)
        self._set('webservice_url', 'https://service.harvestmedia.net/HMP-WS.svc', **kwargs)

        if self.api_key is None:
            raise exceptions.MissingParameter('You must pass api_key to Client')

        self.config = Config()
        self.config.webservice_url = self.webservice_url
        self.request_service_token()
        self.get_service_info()

    @property
    def debug_level(self):
        return self._debug_level

    @debug_level.setter
    def debug_level(self, value):
        self._debug_level = value
        logger.setLevel(value)

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
            logger.debug('HTTP: non 200 status received from server: ' + str(response_status))

            exc = exceptions.InvalidAPIResponse('non 200 HTTP error returned from server: ' + str(response_status) + ': ' + str(response_body))
            exc.code = response.status
            raise exc

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
                    raise exceptions.InvalidToken()
                elif code.text == '6':
                    raise exceptions.InvalidLoginDetails()
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

        logger.debug("url: %s://%s%s" % (self.config.webservice_url_parsed.scheme, self.config.webservice_host, method_uri))

        response = http.getresponse()

        return self._handle_response(response)

    def post_xml(self, method_uri, xml_post_body):
        method_url = self.config.webservice_url + self.__add_service_token(method_uri)

        if self.config.webservice_url_parsed.scheme == 'http':
            http = httplib.HTTPConnection(self.config.webservice_host)
        elif self.config.webservice_url_parsed.scheme == 'https':
            http = httplib.HTTPSConnection(self.config.webservice_host)

        logger.debug("url: " + method_url)
        logger.debug("posting XML: " + xml_post_body)

        http.request('POST', method_url, xml_post_body, {'Content-Type': 'application/xml'}) 

        response = http.getresponse()
        return self._handle_response(response)

    def request_service_token(self):
        method_uri = '/getservicetoken/' + self.api_key

        root = self.get_xml(method_uri)
        xml_token = root.find('token')

        if xml_token is None:
            raise exceptions.InvalidAPIResponse('server did not return token')

        logger.debug('got token: %s (expires: %s)' % (xml_token.get('value'), xml_token.get('expiry')))
        token = xml_token.get('value')
        expiry = xml_token.get('expiry')

        self.config.service_token = ServiceToken(self.config, token, expiry)


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
