# -*- coding: utf-8 -*-

class HarvestMediaError(Exception):
    def __init__(self, reason):
        super(HarvestMediaError, self).__init__(reason)


class APITimeoutError(HarvestMediaError):
    pass

class InvalidAPIResponse(HarvestMediaError):
    def __init__(self, reason):
        super(HarvestMediaError, self).__init__(reason)
        self.code = None

class MissingParameter(HarvestMediaError):
    pass


class IncorrectInputData(HarvestMediaError):
    def __init__(self, reason):
        super(HarvestMediaError, self).__init__(reason)

class InvalidToken(HarvestMediaError):
    def __init__(self):
        super(HarvestMediaError, self).__init__('Invalid Token')

class MemberDoesNotExist(HarvestMediaError):
    def __init__(self):
        super(HarvestMediaError, self).__init__('Member does not exist')

class CorruptInputData(HarvestMediaError):
    def __init__(self):
        super(HarvestMediaError, self).__init__('Corrupt Input Data')
    
    
