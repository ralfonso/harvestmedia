class Track(object):
    """ Represents a Harvest Media track asset """

    def __init__(self, track_element):
        """ Create a new Track object from an ElementTree.Element object

        track_element: the ElementTree.Element object to parse

        """

        for attribute, value in track_element.items():
            setattr(self, attribute, value)
 
    def as_dict(self):
        return dict([(k,v) for k in self.__dict__.items()])
