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

    def __init__(self, reason='Invalid Token'):
        super(HarvestMediaError, self).__init__(reason)


class InvalidLoginDetails(HarvestMediaError):

    def __init__(self, reason="Invalid Login"):
        super(HarvestMediaError, self).__init__(reason)


class MemberDoesNotExist(HarvestMediaError):

    def __init__(self, reason="Member Does Not Exist"):
        super(HarvestMediaError, self).__init__(reason)


class CorruptInputData(HarvestMediaError):
    def __init__(self, reason="Corrupt Input Data"):
        super(HarvestMediaError, self).__init__(reason)


class TokenExpired(Exception):

    pass
