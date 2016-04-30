"""Module to deal with exceptions in the PXE part"""


class Error(Exception):
    """Class to deal with it"""

    def __init__(self, message):
        self.message = message


class InputError(Error):
    """Dummy class"""

    pass
