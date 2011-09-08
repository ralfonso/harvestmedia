# -*- coding: utf-8 -*-
from urlparse import urlparse

class Config(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.service_token = None
            cls._instance.service_token_expires = None
            cls._instance.album_art_url = None
            cls._instance.waveform_url = None
            cls._instance._webservice_url = None
            cls._instance.webservice_url_parsed = None
            cls._instance.debug = None

        return cls._instance

    @property
    def webservice_url(self):
        return self._webservice_url

    @webservice_url.setter
    def webservice_url(self, value):
        self.webservice_url_parsed = urlparse(value)
        self._webservice_url = value
        self.webservice_prefix = self.webservice_url_parsed.path
        self.webservice_host = self.webservice_url_parsed.netloc
