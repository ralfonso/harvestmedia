import xml.etree.cElementTree as ET
from urllib2 import urlopen

from library import Library
from album import Album
from track import Track

class Client(object):
    """

    """

    def __init__(self, api_key, webservice_url):
        """
        initialize the Client object

        api_key: the Harvest Media API key to use
        webservice_url: the base Harvest Media API URL
        """

        self.api_key = api_key
        self.webservice_url = webservice_url
        self.libraries = []
        self.albums = {}
        self.albums_by_id = {}
        
        self.request_service_token()

    def get_remote_xml_root(self, method_url):
        xml_doc = urlopen(method_url)
        try:
            tree = ET.parse(xml_doc)
        except (ET.ParseError, e):
            raise InvalidAPIResponse, "Unable to read the XML from the API server: " + e.message

        root = tree.getroot()
        return root

    def request_service_token(self):
        method_url = self.webservice_url + '/getservicetoken/' + self.api_key
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expires')
    
    def get_libraries(self):
        # reset the stored library list
        self.libraries = {}

        method_url = self.webservice_url + '/getlibraries/' + self.service_token
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        libraries = root.find('libraries').getchildren()
        for library_element in libraries:
            library = Library(self, library_element)
            self.libraries[library.id] = library

        return self.libraries.values()

    def get_library_by_id(self, id, force_reload=False):
        if self.libraries is None or force_reload:
            self.get_libraries()

        return self.libraries[id]


