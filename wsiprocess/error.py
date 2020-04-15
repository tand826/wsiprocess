# -*- coding: utf-8 -*-
"""Custom errors for wsiprocess.
"""


class WsiProcessError(Exception):
    """Root error class.

    Args:
        message (str): Message to show in the stdout.
    """
    def __init__(self, message):
        self.message = message


class SlideLoadError(WsiProcessError):
    """Error on loading slides.

    Args:
        message (str): Message to show in the stdout.
    """
    def __init__(self, message):
        super().__init__(message)


class MissCombinationError(WsiProcessError):
    """Error of the combination of the method and the anntoation file.

    Args
        message (str): Message to show in the stdout.
    """
    def __init__(self, message):
        super().__init__(message)


class PatchSizeTooSmallError(WsiProcessError):
    """Error of the size of patches.

    This should be warning?

    Args:
        message (str): Message to show in the stdout.
    """
    def __init__(self, message):
        super().__init__(message)


class SizeError(WsiProcessError):
    """Error of sizes.

    The slide size is larger than the patches, and the patch size is larger
    than the overlap size.

    Args:
        message (str): Message to show in the stdout.
    """
    def __init__(self, message):
        super().__init__(message)
