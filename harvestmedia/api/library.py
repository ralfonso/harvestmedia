
from util import DictObj
from album import Album

class Library(DictObj):
    
    def __init__(self, library_element):
        self.id = library_element.get('id')
        self.detail = library_element.get('detail')
        self.name = library_element.get('name')


