# -*- coding: utf-8 -*-
import os
from nose.tools import raises, with_setup
from unittest.case import SkipTest
from urllib2 import urlopen
import xml.etree.cElementTree as ET
import StringIO

import mock
import datetime, hashlib

from setup import init_client

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.category import Category

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_categories(HTTPMock):
    cwd = os.path.dirname(__file__)
    categories = open(os.path.join(cwd, 'categories.xml'))
    return_values = [
                        categories.read(),
                    ]
                        
    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response

    http = HTTPMock()
    http.getresponse.side_effect = side_effect
    categories = Category.get_categories()
