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

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_categories(HttpMock):
    client = init_client()
    cwd = os.path.dirname(__file__)
    categories_xml = ET.parse(os.path.join(cwd, 'categories.xml'))

    http = build_http_mock(HttpMock, content=ET.tostring(categories_xml.getroot()))
    categories = Category.query.get_categories(client)

    categories_in_xml = len(categories_xml.getroot().find('categories').findall('category'))
    client_categories = len(categories)
    assert categories_in_xml == client_categories, 'Category counts do not match %s != %s' % \
                                                    (categories_in_xml, client_categories)
