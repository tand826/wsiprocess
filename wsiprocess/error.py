class WsiProcessError(Exception):
    def __init__(self, message):
        self.message = message


class SlideLoadError(WsiProcessError):
    def __init__(self, message):
        super().__init__(message)


class MissCombinationError(WsiProcessError):
    def __init__(self, message):
        super().__init__(message)


class PatchSizeTooSmallError(WsiProcessError):
    def __init__(self, message):
        super().__init__(message)


class SizeError(WsiProcessError):
    def __init__(self, message):
        super().__init__(message)
