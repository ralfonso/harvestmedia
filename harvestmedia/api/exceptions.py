class HarvestMediaError(Exception):
    def __init__(self, reason):
        super(PyBrightcoveError, self).__init__(reason)


class APITimeoutError(HarvestMediaError):
    pass

class InvalidAPIResponse(HarvestMediaError):
    pass
