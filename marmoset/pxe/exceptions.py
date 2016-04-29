class Error(Exception):

    def __init__(self, message):
        self.message = message


class InputError(Error):
    pass
