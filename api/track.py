import pdb


class Track(object):
    """ Represents a Harvest Media track asset """

    def __init__(self, track_element, client):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        self.client = client

        for attribute, value in track_element.items():
            setattr(self, attribute, value)

        pdb.set_trace()
