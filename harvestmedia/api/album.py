class Album(object):
    
    def __init__(self, album_element):
        for attribute, value in album_element.items():
            setattr(self, attribute, value)

    def as_dict(self):
        return dict([(k,v) for k,v in self.__dict__.items()])
