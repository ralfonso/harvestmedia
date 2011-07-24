import harvestmedia
import xml.etree.cElementTree as ET
from urllib2 import urlopen

from library import Library
from album import Album

class Client(object):
    """

    """

    def __init__(self, api_key, webservice_url):
        self.api_key = api_key
        self.webservice_url = webservice_url
        self.libraries = []
        
        self.get_service_token()

    def get_service_token(self):
        method_url = harvestmedia.webservice_url + '/getservicetoken/' + self.api_key
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        token = root.find('token')
        self.service_token = token.get('value')
        self.service_token_expires = token.get('expires')
    
    def get_libraries(self):
        # reset the stored library list
        self.libraries = []

        method_url = self.webservice_url + '/getlibraries/' + self.service_token
        tree = ET.parse(urlopen(method_url))
        root = tree.getroot()
        libraries = root.find('libraries').getchildren()
        for library_element in libraries:
            library = Library(library_element, self)
            self.libraries.append(library) 

        return self.libraries

    def get_library_by_id(self, id, force_reload=False):
        if self.libraries is None or force_reload:
            self.get_libraries()

        for library in self.libraries:
            if library.id == id:
                return library
