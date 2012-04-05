# -*- coding: utf-8 -*-
import logging
import httplib2
import xml.etree.cElementTree as ET

from .config import Config, ServiceToken
import exceptions


logger = logging.getLogger('harvestmedia')


class Client(object):

    """This class handles all HTTP interaction with the Harvest
    Media API.

    :param api_key: the Harvest Media API key to use
    :param debug_level: a Python logging debug level to use for the HM logger
    :param webservice_url: the base Harvest Media API URL
    """

    def __init__(self, api_key, debug_level='INFO',
                    webservice_url='https://service.harvestmedia.net/HMP-WS.svc'):

        self.api_key = api_key
        self.debug_level = debug_level
        self.webservice_url = webservice_url

        self.config = Config(debug_level=debug_level, webservice_url=webservice_url)
        self.request_service_token()
        self.get_service_info()

    @property
    def debug_level(self):
        return self._debug_level

    @debug_level.setter
    def debug_level(self, value):
        self._debug_level = value
        logger.setLevel(value)

    def _add_service_token(self, uri):
        if '{{service_token}}' not in uri:
            return uri

        try:
            service_token = self.config.service_token.token
        except exceptions.TokenExpired:
            self.request_service_token()
            service_token = self.config.service_token.token

        uri = uri.replace('{{service_token}}', service_token)

        return uri

    def _build_url(self, path):
        return self.config.webservice_url + self._add_service_token(path)

    def _handle_response(self, response, content):
        if response.status != 200:
            response_status = response.status
            logger.debug('HTTP: non 200 status received from server: ' + str(response_status))

            exc = exceptions.InvalidAPIResponse('non 200 HTTP error returned from server: ' + \
                                                 str(response_status) + ': ' + str(content))
            exc.code = response.status
            raise exc

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("server response: " + str(content))

        try:
            root = ET.fromstring(content)
        except ET.ParseError, e:
            raise exceptions.InvalidAPIResponse, \
                            "Unable to read the XML from the API server: " + e.message

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
        """Called by the model classes to perform an HTTP GET and receive
        XML from the HM API

        """

        method_url = self._build_url(method_uri)
        http = httplib2.Http()
        response, content = http.request(method_url, 'GET')

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('get_xml url: %s' % method_url)

        return self._handle_response(response, content)

    def post_xml(self, method_uri, xml_post_body):
        """Called by the model classes to perform an HTTP POST and receive
        XML from the HM API

        """

        method_url = self._build_url(method_uri)
        http = httplib2.Http()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('post_xml url: %s' % method_url)
            logger.debug("posting XML: " + xml_post_body)

        response, content = http.request(method_url, 'POST', xml_post_body, {'Content-Type': 'application/xml'})
        return self._handle_response(response, content)

    def request_service_token(self):
        """Uses the API key to get a valid service token from the HM api.
        Service tokens are used for every call to the API, embedded in the URL

        This method is called automatically on client init
        """

        method_uri = '/getservicetoken/' + self.api_key

        root = self.get_xml(method_uri)
        xml_token = root.find('token')

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('got token: %s (expires: %s)' % \
                (xml_token.get('value'), xml_token.get('expiry')))

        token = xml_token.get('value')
        expiry = xml_token.get('expiry')

        self.config.service_token = ServiceToken(self.config, token, expiry)

    def get_service_info(self):
        """Gets the service info for the current HM account.
        Service info includes URLs for album art, waveforms,
        music streaming, and music downloading

        This method is called automatically on client init

        """

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
