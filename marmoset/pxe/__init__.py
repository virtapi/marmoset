"""Base file for PXE interaction"""
from .client_config import ClientConfig
from .label import Label


def create(args):
    """Creates a new PXE entry"""
    pxe_client = ClientConfig(args.ip_address, args.password, args.script,
                              args.uuid, args.ipv6_address, args.ipv6_gateway,
                              args.ipv6_prefix)
    used_options = pxe_client.create(Label.find(args.label))

    msg = 'Created %s with following Options: %s'

    print(msg % (pxe_client.file_path(), " ".join(used_options)))


def dolist(args):
    """List all PXE entries"""
    # pylint: disable-msg=unused-argument
    for pxe_client in ClientConfig.all():
        print('%s: %s' % (pxe_client.ip_address, pxe_client.label))


def remove(args):
    """Remove a specific PXE entry"""
    pxe_client = ClientConfig(args.ip_address)
    if pxe_client.remove():
        print('Removed', pxe_client.file_path())
    else:
        print('No entry found for', pxe_client.ip_address)
