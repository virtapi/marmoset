"""File for dealing with PXE lables"""
from .client_config import ClientConfig
from .exceptions import InputError


class Label:
    """class to handle PXE lables"""

    instances = []

    @classmethod
    def find(cls, name):
        """Return the instance with the given name."""
        for i in cls.instances:
            if name == i.name:
                return i
        raise InputError("No PXELabel with name '%s' found." % (name,))

    @classmethod
    def names(cls):
        """Return the names of all instances of the class."""
        return [x.name for x in cls.instances]

    def __init__(self, name, callback=None):
        if callback in (None, ''):
            callback = None
        elif not ClientConfig.has_callback(callback):
            msg = "Callback method '%s' doesn't exist. Available: %s"
            callbacklist = ', '.join(ClientConfig.callbacks())
            raise InputError(msg % (callback, callbacklist))

        self.__class__.instances.append(self)
        self.name = name
        self.callback = callback
