# -*- coding: utf-8 -*-
from urlparse import urlparse
import datetime
import iso8601
import pytz
import logging
from exceptions import TokenExpired
from signals import signals

logger = logging.getLogger('harvestmedia')

class ServiceToken(object):
    def __init__(self, config, token, expiry):
        self._token = None
        self._expiry = None
        self._expiry_dt = None
        
        self.config = config
        self.expiry = expiry
        self.token = token

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        # convert from the harvestmedia timezone to UTC
        service_token_expires_date = iso8601.parse_date(value)
        hm_tz = pytz.timezone(self.config.timezone)
        service_token_expires_date = service_token_expires_date.replace(tzinfo=hm_tz)
        utc_tz =  pytz.timezone('UTC')
        self._expiry_dt = service_token_expires_date.astimezone(utc_tz)
        self._expiry = value

    @property
    def token(self):
        utc_now = datetime.datetime.now(pytz.utc)
        if self._expiry_dt <= utc_now:
            logger.debug('%s <=> %s' % (self._expiry_dt, utc_now))
            raise TokenExpired

        return self._token

    @token.setter
    def token(self, value): 
        self._token = value 

class Config(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # set up some defaults
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.service_token = None
            cls._instance.service_token_expires = None
            cls._instance.album_art_url = None
            cls._instance.waveform_url = None
            cls._instance._webservice_url = None
            cls._instance.webservice_url_parsed = None
            cls._instance.debug = None
            cls._instance.timezone = 'Australia/Sydney'

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
