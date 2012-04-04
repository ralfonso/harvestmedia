# -*- coding: utf-8 -*-
import datetime
import hashlib
import mock
from nose.tools import raises
import os
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.category import Category

from setup import init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_categories(HTTPMock):
    client = init_client()
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
    categories = Category.query.get_categories(client)
