"""file for dealing with PXE client configs"""
import base64
import crypt
import os
import re
from string import Template as Stringtemplate
from textwrap import dedent
from uuid import UUID, uuid4
from marmoset import validation
from .exceptions import Error


class ClientConfig:
    """Class to handle PXE configs for clients"""

    CFG_DIR = '/srv/tftp/pxelinux.cfg/'

    CFG_TEMPLATE = Stringtemplate(dedent('''\
        INCLUDE pxelinux.cfg/linux
        DEFAULT instantboot
        PROMPT 0
        TIMEOUT 1
        LABEL instantboot
            KERNEL cmd.c32
            APPEND ${label} ${options}
        '''))

    @classmethod
    def all(cls):
        """Return all currently defined client configs."""
        entries = []
        for entry_file in os.listdir(ClientConfig.CFG_DIR):
            if re.match('[0-9A-Z]{8}', entry_file):
                entries.append(ClientConfig(entry_file))
        return entries

    @classmethod
    def has_callback(cls, name):
        """Return if the class provides the given callback method."""
        return name in cls.callbacks()

    @classmethod
    def callbacks(cls):
        """List all available callback methods."""
        cbs = []
        for method in dir(cls):
            if method[:3] == 'cb_':
                cbs.append(method[3:])
        return cbs

    # pylint: disable-msg=too-many-arguments
    def __init__(self, ip_address, password=None, script=None, uuid=None,
                 ipv6_address=None, ipv6_gateway=None, ipv6_prefix=None,
                 persistent=False):
        """
        Initialize a PXE config object with provided data

        We do a lot of data validation here. Besides that we do a lot of
        assumptions her. Example: IPv6 is a all-or-nothing setup. All IPv6
        params are mandatory.
        """
        if re.match('[0-9A-Z]{8}', ip_address.upper()):
            octets = [str(int(x, 16)) for x in re.findall('..', ip_address)]
            ip_address = '.'.join(octets)
            get_mode = True
        else:
            get_mode = False

        self.ip_address = ip_address
        self.script = script

        # set ipv6 parameters only when all are provided
        if (ipv6_address and ipv6_gateway and ipv6_prefix) is not None:
            self.ipv6_address = ipv6_address
            self.ipv6_gateway = ipv6_gateway
            self.ipv6_prefix = ipv6_prefix
        else:
            self.ipv6_address = None
            self.ipv6_gateway = None
            self.ipv6_prefix = None

        # if uuid is passed, validate it. In case validation fails
        # a new uuid is generated
        if uuid is None:
            self.uuid = None
        else:
            if validation.is_uuid(uuid):
                self.uuid = str(UUID(uuid))
            else:
                self.uuid = str(uuid4())

        if self.exists():
            self.label = self.get_label()

            if (self.ipv6_address and self.ipv6_gateway and
                    self.ipv6_prefix) is None:
                self.ipv6_address = self.get_ipv6_address()
                self.ipv6_gateway = self.get_ipv6_gateway()
                self.ipv6_prefix = self.get_ipv6_prefix()

            if script is None:
                self.script = self.get_script()

            # fetch uuid from config file only in get_mode, we don't want
            # to reuse and old uuid if none was passed
            if get_mode:
                self.uuid = self.get_uuid()

        if password not in [None, '']:
            self.password = password

        self.persistent = persistent

    def exists(self):
        """Return if there is a config file for this instance."""
        return os.path.isfile(self.file_path())

    def get_label(self):
        """Parse the label from the config file."""
        with open(self.file_path()) as file:
            for line in file:
                option = re.match(r' *APPEND (\w+)', line)
                if option is not None:
                    return option.group(1)

    def get_script(self):
        """Parse the script option from the config file."""
        with open(self.file_path()) as file:
            for line in file:
                option = re.match(r' *APPEND.*script=(\S+)', line)
                if option is not None:
                    return option.group(1)

    def get_uuid(self):
        """Parse the uuid option from the config file."""
        with open(self.file_path()) as file:
            for line in file:
                option = re.match(r' *APPEND.*UUID=(\S+)', line)
                if option is not None:
                    return option.group(1)

    def get_ipv6_address(self):
        """Parse the ipv6 address option from the config file."""
        ipv6_address = self.get_from_config('IP6ADDR')
        return ipv6_address

    def get_ipv6_gateway(self):
        """Parse the ipv6 gateway option from the config file."""
        ipv6_gateway = self.get_from_config('IP6GW')
        return ipv6_gateway

    def get_ipv6_prefix(self):
        """Parse the ipv6 prefix option from the config file."""
        ipv6_prefix = self.get_from_config('IP6PRE')
        return ipv6_prefix

    def get_from_config(self, option_string):
        """Parse the defined option from the config file."""
        with open(self.file_path()) as file:
            for line in file:
                option = re.match(r' *APPEND.*%s=(\S+)' % option_string, line)
                if option is not None:
                    return option.group(1)

    def create(self, pxe_label):
        """Create the config file for this instance."""
        options = []
        if pxe_label.callback is not None:
            func = getattr(self, 'cb_%s' % pxe_label.callback)

            if func is None:
                print("No password hash method with name %s found" % func)

            options.append(func())

        if self.script is not None:
            options.append("script=%s" % self.script)

        if self.uuid is not None:
            options.append("UUID=%s" % self.uuid)

        if (self.ipv6_address and self.ipv6_gateway and
                self.ipv6_prefix) is not None:
            options.append("IP6ADDR=%s" % self.ipv6_address)
            options.append("IP6GW=%s" % self.ipv6_gateway)
            options.append("IP6PRE=%s" % self.ipv6_prefix)

        content = self.__expand_template(pxe_label.name, options)
        self.__write_config_file(content)
        self.label = pxe_label.name

        return options

    def remove(self):
        """Remove the config file for this instance."""
        if self.exists():
            self.__make_file_mutable(self.file_path())
            os.remove(self.file_path())
            return True
        return False

    def file_name(self):
        """Return the file name in the PXE file name style."""
        octets = map(int, self.ip_address.split('.'))
        return "%02X%02X%02X%02X" % tuple(octets)

    def file_path(self, name=None):
        """Return the path to the config file of th instance."""
        if name is None:
            name = self.file_name()

        cfgdir = ClientConfig.CFG_DIR.rstrip('/')
        return cfgdir + '/' + name

    def __write_config_file(self, content, path=None):
        if path is None:
            path = self.file_path()

        # pylint seems to be wrong on this one
        # pylint: disable-msg=unexpected-keyword-arg
        os.makedirs(ClientConfig.CFG_DIR, exist_ok=True)
        self.__make_file_mutable(path)
        with open(path, 'w') as file:
            file.write(content)
        if self.persistent is True:
            self.__make_file_immutable(path)

    def __make_file_immutable(self, path=None):
        if path is None:
            path = self.file_path()
        if os.path.isfile(path):
            return_code = os.system('chattr +i {path}'.format(path=path))
            if return_code > 0:
                raise Error(message='couldnt set immutable flag for {path}'.
                            format(path=path))

    def __make_file_mutable(self, path=None):
        if path is None:
            path = self.file_path()
        if os.path.isfile(path):
            return_code = os.system('chattr -i {path}'.format(path=path))
            if return_code > 0:
                raise Error(message='couldnt remove immutable flag for {path}'.
                            format(path=path))

    def __expand_template(self, label, options=None):
        """Return the config file content expanded with the given values."""
        if options is not None:
            options = " ".join(options)
        else:
            options = ''

        template = ClientConfig.CFG_TEMPLATE
        return template.substitute(label=label,
                                   options=options)

    def __mkpwhash(self):
        """
        Return the hashed password.

        The password attribute is set if not present.
        """
        if 'password' not in vars(self) or self.password in [None, '']:
            password = base64.b64encode(os.urandom(16), b'-_')[:16]
            self.password = password.decode('utf-8')
        return crypt.crypt(self.password, self.__mksalt())

    def __mksalt(self):
        """Return a crypt style salt string."""
        return crypt.mksalt(crypt.METHOD_SHA512)

    def cb_setpwhash(self):
        """Callback that adds a HASH= string to the command line."""
        return 'HASH=' + self.__mkpwhash()

    def cb_createpwhashfile(self):
        """Callback that creates a password hash file."""
        file_path = self.file_path('PWHASH.' + self.ip_address)
        self.__write_config_file(self.__mkpwhash(), file_path)
        return None
