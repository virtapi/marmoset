from os import path
import configparser
import warnings
import socket

PATH = path.join(path.dirname(__file__), '../marmoset.conf')

def default():
    config = configparser.ConfigParser()

    config['Common'] = dict(
        FQDN=socket.getfqdn()
    )

    config['Modules'] = dict(
        Webserver = 'True',
        PXE = 'True',
        VM = 'True'
    )

    config['Webserver'] = dict(
        Username    = 'admin',
        Password    = 'secret',
        BasicRealm  = __name__
    )

    config['PXEConfig'] = dict(
        ConfigDirectory = '/srv/tftp/pxelinux.cfg'
    )

    config['PXELabel']  = dict(
    )

    config['Libvirt']   = dict(
        URI = 'qemu:///system',
        Network = 'internet',
        StoragePool = 'storage'
    )
    return config

def read_file(file_path = None):
    global PATH
    config = default()
    if file_path is None:
        file_path = PATH
    if path.isfile(file_path):
        config.read(file_path)
    else:
        warnings.warn('config file not found: {}'.format(file_path))
    return config

def load(file_path = None):
    config = read_file(file_path)

    if config['Modules'].getboolean('PXE'):
        from . import pxe

        if config.options('PXELabel').__len__() == 0:
            raise Exception('No PXELabel defined in config')

        # Create pxe label list.
        [pxe.Label(n, cb) for n, cb in config['PXELabel'].items()]
        pxe.ClientConfig.CFG_DIR = config['PXEConfig'].get('ConfigDirectory')


    if config['Modules'].getboolean('VM'):
        from . import virt

        if config['Libvirt'].get('XMLTemplateDirectory'):
            virt.Virt.TEMPLATE_DIR = config['Libvirt']['XMLTemplateDirectory']

        virt.base.URI           = config['Libvirt'].get('URI')
        virt.Network.DEFAULT    = config['Libvirt'].get('Network', 'default')
        virt.Storage.DEFAULT    = config['Libvirt'].get('Storage', 'default')

    if config['Modules'].getboolean('Webserver'):
        from . import webserver
        webserver.config = config

    return config

