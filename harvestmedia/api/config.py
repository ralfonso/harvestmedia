# -*- coding: utf-8 -*-

class Config(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.service_token = None
            cls._instance.album_art_url = None
            cls._instance.waveform_url = None

        return cls._instance
