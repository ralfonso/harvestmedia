# -*- coding: utf-8 -*-
import datetime
import iso8601
import logging
import pytz
from urlparse import urlparse

from .exceptions import TokenExpired


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
        utc_tz = pytz.timezone('UTC')
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

    def _set(self, param, default=None, **kwargs):
        if kwargs.get(param, None):
            setattr(self, param, kwargs[param])
        else:
            setattr(self, param, default)

    def __init__(self, *args, **kwargs):
        self._set('waveform_url', **kwargs)
        self._set('webservice_url', **kwargs)
        self._set('debug_level', **kwargs)
        self._set('timezone', 'Australia/Sydney', **kwargs)

    @property
    def webservice_url(self):
        return self._webservice_url

    @webservice_url.setter
    def webservice_url(self, value):
        self.webservice_url_parsed = None

        if value is not None:
            self.webservice_url_parsed = urlparse(value)
            self._webservice_url = value
            self.webservice_prefix = self.webservice_url_parsed.path
            self.webservice_host = self.webservice_url_parsed.netloc
