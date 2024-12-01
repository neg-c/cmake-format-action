import traceback

class CMakeFormatError(Exception):
    """Base exception for all cmake-format errors"""
    pass

class DiffError(CMakeFormatError):
    def __init__(self, message, errs=None):
        super().__init__(message)
        self.errs = errs or []

class UnexpectedError(CMakeFormatError):
    def __init__(self, message, exc=None):
        super().__init__(message)
        self.formatted_traceback = traceback.format_exc()
        self.exc = exc