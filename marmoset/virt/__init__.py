"""initial file for dealing with virtualization"""
import uuid
from pprint import pprint

from .domain import Domain
from .network import Network
from .storage import Storage


def create(args):
    """creates a libvirt domain"""
    network = Network.find_by('name', Network.DEFAULT)
    if network.knows_ip_address(args.ip_address):
        raise Exception('IP address already assigned')

    name = "{}_{}".format(args.user, args.name)
    storage = Storage.find_by('name', Storage.DEFAULT)
    disk = storage.create_volume(name, args.disk)
    memory, unit = base.parse_unit(args.memory)

    domain = Domain.define(
        uuid=str(uuid.uuid4()),
        name=args.name,
        user=args.user,
        memory=memory,
        unit=unit,
        vcpu=args.cpu,
        disks=[dict(path=disk.path, bus='virtio', target='hda')],
        interfaces=[dict(model='virtio', network=Network.DEFAULT)],
        password=args.get('password', base.generate_password)
    )

    network.add_host(
        domain.interfaces[0].mac_address,
        args.ip_address,
        name
    )

    return domain


def list(args):
    """list all domains"""
    for domain in Domain.all():
        pprint(domain.attributes())


def edit(domain, args):
    """edit a specific domain"""
    memory, unit = base.parse_unit(args.get('memory', domain.memory))
    return Domain.define(
        name=domain.name,
        user=domain.user,
        memory=memory,
        unit=unit,
        vcpu=args.get('cpu', domain.vcpu),
        disks=[d.attributes() for d in domain.disks],
        interfaces=[i.attributes() for i in domain.interfaces],
        password=args.get(
            'password',
            domain.vnc_data.get('password', base.generate_password())
        ),
        uuid=domain.uuid
    )


def remove(args):
    """remove a specific domain"""
    domain = Domain.find_by('uuid', args.uuid)
    try:
        domain.shutdown()
    except:
        pass
    for interface in domain.interfaces:
        host = interface.host()
        if host is not None:
            host.delete()
    if domain.undefine():
        print('Removed', domain.name())
