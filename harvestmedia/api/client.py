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
        self.libraries = []
        
        self.request_service_token()

    def get_remote_xml_root(self, method_uri):
        method_url = self.webservice_url + method_uri % {'service_token': self.service_token}
        xml_doc = urlopen(method_url)
        try:
            tree = ET.parse(xml_doc)
        except (ET.ParseError, e):
            raise exceptions.InvalidAPIResponse, "Unable to read the XML from the API server: " + e.message

        root = tree.getroot()
        return root

    def request_service_token(self):
        method_url = self.webservice_url + '/getservicetoken/' + self.api_key
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expires')


class APIClient(Client):
    def __init__(self, api_key=None, webservice_url=None):
        super(APIClient, self).__init__(api_key=api_key, webservice_url=webservice_url)
        if not hasattr(self, "api_key"):
            raise exceptions.NotConfiguredError("Please specify an api_key")

        if not hasattr(self, "webservice_url"):
            raise exceptions.NotConfiguredError("Please specify the webservice_url")
