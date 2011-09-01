# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import httplib

import exceptions
import config
import logging

logging.basicConfig(level=logging.DEBUG)
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

        self.libraries = []
        
        if not self.config.service_token:
            self.config.service_token = self.request_service_token()

        if not self.config.album_art_url:
            self.get_service_info()

    def __add_service_token(self, uri):
        if hasattr(self, 'service_token') and self.service_token:
            uri = uri.replace('{{service_token}}', self.service_token)

        return uri

    def get_remote_xml_root(self, method_uri):
        method_uri = self.config.webservice_prefix + self.__add_service_token(method_uri)
        if self.config.webservice_url_parsed.scheme == 'http':
            http = httplib.HTTPConnection(self.config.webservice_host)
        elif self.config.webservice_url_parsed.scheme == 'https':
            http = httplib.HTTPSConnection(self.config.webservice_host)
        http.request('GET', method_uri)

        if self.debug:
            logger.debug("url: %s://%s%s" % (self.config.webservice_url_parsed.scheme, self.config.webservice_host, method_uri))

        response = http.getresponse()
        xml_doc_str = response.read()

        if self.debug:
            logger.debug("server response: " + xml_doc_str.decode('utf_16_le'))

        try:
            root = ET.fromstring(xml_doc_str)
        except ET.ParseError, e:
            raise exceptions.InvalidAPIResponse, "Unable to read the XML from the API server: " + e.message

        return root

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
        if response.status != 200:
            response_status = response.status
            response_body = response.read()

            if self.debug:
                logger.debug('non 200 HTTP error returned from server: ' + str(response_status) + ': ' + str(response_body))

            raise exceptions.InvalidAPIResponse('non 200 HTTP error returned from server: ' + str(response_status) + ': ' + str(response_body))

        xml_doc_str = response.read()

        if self.debug:
            logger.debug("response XML: " + xml_doc_str)
        return xml_doc_str
            

    def request_service_token(self):
        method_uri = '/getservicetoken/' + self.api_key

        root = self.get_remote_xml_root(method_uri)
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expiry')

        return self.service_token

    def get_service_info(self):
        method_uri = '/getserviceinfo/{{service_token}}'

        root = self.get_remote_xml_root(method_uri)
        asset_url = root.find('asseturl')
        self.config.album_art_url = asset_url.get('albumart')
        self.config.waveform_url = asset_url.get('waveform')

class APIClient(Client):
    def __init__(self, api_key=None, webservice_url=None):
        super(APIClient, self).__init__(api_key=api_key, webservice_url=webservice_url)
        if not self.api_key:
            raise exceptions.NotConfiguredError("Please specify an api_key")

        if not self.webservice_url:
            raise exceptions.NotConfiguredError("Please specify the webservice_url")
