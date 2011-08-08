# -*- coding: utf-8 -*-

class HarvestMediaError(Exception):
    def __init__(self, reason):
        super(HarvestMediaError, self).__init__(reason)


class APITimeoutError(HarvestMediaError):
    pass

class InvalidAPIResponse(HarvestMediaError):
    pass

class MissingParameter(HarvestMediaError):
    pass
