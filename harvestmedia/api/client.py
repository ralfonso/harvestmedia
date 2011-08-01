# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from urllib2 import urlopen

import exceptions
import config

class Client(object):
    """

    """

    
    def _set(self, param, default=None, **kwargs):
        if kwargs.get(param, None):
            setattr(self, param, kwargs[param])
        elif self.config.__dict__.has_key(param):
            setattr(self, param, self.config.__dict__[param])
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
        self.libraries = []
        
        if not self.config.service_token:
            self.config.service_token = self.request_service_token()

        if not self.config.album_art_url:
            self.get_service_info()

    def get_remote_xml_root(self, method_uri):
        if hasattr(self, 'service_token'):
            params = {'service_token': self.service_token}
        else:
            params = {}

        method_url = self.webservice_url + method_uri % params
        xml_doc = urlopen(method_url)
        xml_doc_str = xml_doc.read()

        try:
            root = ET.fromstring(xml_doc_str)
        except ET.ParseError, e:
            raise exceptions.InvalidAPIResponse, "Unable to read the XML from the API server: " + e.message

        return root

    def request_service_token(self):
        method_uri = '/getservicetoken/' + self.api_key

        root = self.get_remote_xml_root(method_uri)
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expiry')

        return self.service_token

    def get_service_info(self):
        method_uri = '/getserviceinfo/%(service_token)s'

        root = self.get_remote_xml_root(method_uri)
        asset_url = root.find('asseturl')
        self.config.album_art_url = asset_url.get('albumart')
        self.config.waveform_url = asset_url.get('waveform')

class APIClient(Client):
    def __init__(self, api_key=None, webservice_url=None):
        super(APIClient, self).__init__(api_key=api_key, webservice_url=webservice_url)
        if not hasattr(self, "api_key"):
            raise exceptions.NotConfiguredError("Please specify an api_key")

        if not hasattr(self, "webservice_url"):
            raise exceptions.NotConfiguredError("Please specify the webservice_url")
