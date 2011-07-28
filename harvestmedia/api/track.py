from util import DictObj


class Track(DictObj):
    """ Represents a Harvest Media track asset """

    def __init__(self, client, xml_data=None):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        self.client = client

        if xml_data is not None:
            self._load(xml_data)
 
    def _load(self, xml_data):
        for attribute, value in xml_data.items():
            setattr(self, attribute, value)

    def as_dict(self):
        return dict([(k,v) for k in self.__dict__.items()])
