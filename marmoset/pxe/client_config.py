import os, re, crypt, base64
from textwrap import dedent
from string import Template as Stringtemplate
from uuid import UUID, uuid4
from marmoset import validation


class ClientConfig:

    CFG_DIR = '/srv/tftp/pxelinux.cfg/'

    CFG_TEMPLATE = Stringtemplate(dedent('''\
        INCLUDE ${include}
        DEFAULT instantboot
        PROMPT 0
        TIMEOUT 1
        LABEL instantboot
            KERNEL cmd.c32
            APPEND ${label} ${options}
        '''))

    CFG_INCLUDE = 'pxelinux.cfg/default'

    @classmethod
    def all(cls):
        '''Return all currently defined client configs.'''
        entries = []
        for entry_file in os.listdir(ClientConfig.CFG_DIR):
            if re.match('[0-9A-Z]{8}', entry_file):
                entries.append(ClientConfig(entry_file))
        return entries


    @classmethod
    def has_callback(cls, name):
        '''Return if the class provides the given callback method.'''
        return name in cls.callbacks()


    @classmethod
    def callbacks(cls):
        '''List all available callback methods.'''
        cbs = []
        for m in dir(cls):
            if m[:3] == 'cb_':
                cbs.append(m[3:])
        return cbs

    def __init__(self, ip_address, password=None, script=None, uuid=None):
        if re.match('[0-9A-Z]{8}', ip_address.upper()):
            octets = [str(int(x, 16)) for x in re.findall('..', ip_address)]
            ip_address = '.'.join(octets)
            get_mode = True
        else:
            get_mode = False

        self.ip_address = ip_address
        self.script = script

        # if uuid is passed, validate it. In case validation fails
        # a new uuid is generated
        if uuid is None :
            self.uuid = None
        else:
            if validation.is_uuid(uuid):
                self.uuid = str(UUID(uuid))
            else:
                self.uuid = str(uuid4())

        if self.exists():
            self.label = self.get_label()

            if script is None:
                self.script = self.get_script()

            # fetch uuid from config file only in get_mode, we don't want
            # to reuse and old uuid if none was passed
            if get_mode:
                self.uuid = self.get_uuid()

        if not password in [None, '']:
            self.password = password


    def exists(self):
        '''Return if there is a config file for this instance.'''
        return os.path.isfile(self.file_path())


    def get_label(self):
        '''Parse the label form the config file.'''
        with open(self.file_path()) as f:
            for line in f:
                m = re.match(' *APPEND (\w+)', line)
                if m is not None:
                    return m.group(1)

    def get_script(self):
        '''Parse the script option form the config file.'''
        with open(self.file_path()) as f:
            for line in f:
                m = re.match(' *APPEND.*script=(\S+)', line)
                if m is not None:
                    return m.group(1)

    def get_uuid(self):
        """ Parse the uuid option from the config file."""
        with open(self.file_path()) as f:
            for line in f:
                m = re.match(' *APPEND.*UUID=(\S+)', line)
                if m is not None:
                    return m.group(1)

    def create(self, pxe_label):
        '''Create the config file for this instance.'''
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

        content = self.__expand_template(pxe_label.name, options)
        self.__write_config_file(content)
        self.label = pxe_label.name

        return options


    def remove(self):
        '''Remove the config file for this instance.'''
        if self.exists():
            os.remove(self.file_path())
            return True
        else:
            return False


    def file_name(self):
        '''Return the file name in the PXE file name style.'''
        octets = map(int, self.ip_address.split('.'))
        return "%02X%02X%02X%02X" % tuple(octets)


    def file_path(self, name=None):
        '''Return the path to the config file of th instance.'''
        if name is None:
            name = self.file_name()

        cfgdir = ClientConfig.CFG_DIR.rstrip('/')
        return cfgdir + '/' + name


    def __write_config_file(self, content, path=None):
        if path is None:
            path = self.file_path()

        os.makedirs(ClientConfig.CFG_DIR, exist_ok=True)
        f = open(path, 'w')
        f.write(content)
        f.close()


    def __expand_template(self, label, options = None):
        '''Return the config file content expanded with the given values.'''

        if options is not None:
            options = " ".join(options)
        else:
            options = ''

        template = ClientConfig.CFG_TEMPLATE
        include = ClientConfig.CFG_INCLUDE
        return template.substitute(label=label,
                                   options=options,
                                   include=include)


    def __mkpwhash(self):
        '''Return the hashed password. The password attribute is set if not present.'''
        if 'password' not in vars(self) or self.password in [None, '']:
            pw = base64.b64encode(os.urandom(16), b'-_')[:16]
            self.password = pw.decode('utf-8')
        return crypt.crypt(self.password, self.__mksalt())


    def __mksalt(self):
        '''Return a crypt style salt string.'''
        return crypt.mksalt(crypt.METHOD_SHA512)


    def cb_setpwhash(self):
        '''Callback that adds a HASH= string to the command line.'''
        return 'HASH=' + self.__mkpwhash()


    def cb_createpwhashfile(self):
        '''Callback that creates a password hash file.'''
        file_path = self.file_path('PWHASH.' + self.ip_address)
        self.__write_config_file(self.__mkpwhash(), file_path)
        return None

