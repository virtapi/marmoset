"""Module to deal will all the installimage configs"""
import os
import re
from collections import defaultdict


class InstallimageConfig:
    """Handles installimage configuration for clients"""

    CFG_DIR = '/srv/tftp/installimage/'

    @classmethod
    def all(cls):
        """Return all currently defined installimage configs."""
        entries = []
        for entry_file in os.listdir(InstallimageConfig.CFG_DIR):
            if re.match('([0-9A-Za-z]{2}_){5}[0-9A-Za-z]{2}', entry_file):
                entries.append(InstallimageConfig(entry_file))
        return entries

    def __init__(self, mac):
        """Initialize the attributes properly. Assign provided MAC address"""
        self.variables = defaultdict(list)
        self.mac = mac

        if self.exists():
            self.__read_config_file()

    def add_or_set(self, key, value):
        """Adds a new key/value to the config"""
        if value not in self.variables[key.upper()]:
            self.variables[key.upper()].append(value)

    def clear_variables(self):
        """Clears our variables"""
        self.variables = defaultdict(list)

    def create(self):
        """Writes the config from memory to disk"""
        self.__write_config_file()

    def exists(self):
        """Check if a config is already present on the disk"""
        return os.path.isfile(self.file_path())

    def remove(self):
        """Remove the installimage file for this instance."""
        if self.exists():
            os.remove(self.file_path())
            return True
        return False

    def file_name(self):
        """Return the file name in the Installimage file name style."""
        return self.mac.replace(":", "_").lower()

    def file_path(self, name=None):
        """Return the path to the config file of th instance."""
        if name is None:
            name = self.file_name()

        cfgdir = InstallimageConfig.CFG_DIR.rstrip('/')
        return os.path.join(cfgdir, name)

    def __read_config_file(self, path=None):
        if path is None:
            path = self.file_path()

        lines = []

        with open(path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.strip():
                key = line.split(" ")[0]
                value = line.split(" ", 1)[1].rstrip('\n')

                self.variables[key].append(value)

    def get_content(self):
        """Reads a config and parses it"""
        variable_lines = []
        for key in self.variables:
            for value in self.variables[key]:
                variable_lines.append("%s %s" % (key, value))

        content = "\n".join(variable_lines)

        if not content.endswith("\n"):
            content += "\n"

        return content

    def __write_config_file(self, path=None):
        if path is None:
            path = self.file_path()

        content = self.get_content()

        # pylint is wrong on this one as it seems
        # pylint: disable-msg=unexpected-keyword-arg
        os.makedirs(InstallimageConfig.CFG_DIR, exist_ok=True)
        with open(path, 'w') as file:
            file.write(content)
