from string import Template

from libvirt import libvirtError

from . import base, domain_states
from .exceptions import Error
from .network import Network


class Domain(base.Parent):
    _func = dict(
        all='listAllDomains',
        uuid='lookupByUUIDString',
        id='lookupByID',
        name='lookupByName'
    )

    @classmethod
    def define(cls, **attrs):
        for klass in 'Disk', 'Interface':
            key = klass.lower() + 's'
            klass = getattr(cls, klass)
            res = [klass.xml_template(**r) for r in attrs[key]]
            attrs[key] = '\n'.join(res)
        with open(cls.template_file()) as f:
            xml = Template(f.read()).substitute(attrs)
        with base.connection() as conn:
            return cls(conn.defineXML(xml))

    @property
    def uuid(self):
        return self._resource.UUIDString()

    @property
    def name(self):
        name = self.get_xml('./metadata/marmoset/name')
        return self._resource.name() if name is None else name.text

    @property
    def user(self):
        user = self.get_xml('./metadata/marmoset/user')
        if user is not None:
            return user.text

    @property
    def memory(self):
        return base.with_unit(int(self.get_xml('memory').text) * 1024)

    @property
    def vcpu(self):
        return self.get_xml('vcpu').text

    @property
    def state(self):
        state_id, reason_id = self._resource.state()
        state = domain_states.States[state_id]
        reason = domain_states.Reasons[state][reason_id]
        return dict(state=state, reason=reason)

    @property
    def disks(self):
        disks = self.get_xml('devices').findall('disk')
        return [Domain.Disk(disk, self) for disk in disks]

    @property
    def interfaces(self):
        interfaces = self.get_xml('devices').findall('interface')
        return [Domain.Interface(iface, self) for iface in interfaces]

    @property
    def vnc_data(self):
        graphics = self.get_xml('devices/graphics')
        if graphics is None:
            return {}
        else:
            return dict(
                vnc_port=graphics.attrib.get('port'),
                ws_port=graphics.attrib.get('websocket'),
                password=graphics.attrib.get('passwd')
            )

    def info(self):
        keys = ['state', 'memory_max', 'memory', 'vcpu', 'cpu_time']
        return dict(zip(keys, self._resource.info()))

    def start(self):
        self._command('create')

    def stop(self):
        self._command('destroy')

    def shutdown(self):
        self._command('shutdown')

    def reset(self):
        self._command('reset')

    def undefine(self):
        self._command('undefine')
        self._resource = None

    def _command(self, cmd, *args, **kwargs):
        try:
            func = getattr(self._resource, cmd)
            return func(*args, **kwargs)
        except libvirtError as e:
            raise Error(str(e))

    class Disk(base.Child):

        @property
        def path(self):
            return self._xml.find('source').attrib.get('dev')

        @property
        def target(self):
            return self._xml.find('target').attrib['dev']

        @property
        def type(self):
            return self._xml.attrib['type']

        @property
        def device(self):
            return self._xml.attrib['device']

        @property
        def bus(self):
            return self._xml.find('target').attrib['bus']

        @property
        def capacity(self):
            value = self.blockinfo()['capacity']
            return base.with_unit(value)

        def blockinfo(self):
            keys = ['capacity', 'allocation', 'physical']
            #pylint: disable-msg=protected-access
            values = self._parent._resource.blockInfo(self.target)
            return dict(zip(keys, values))

    class Interface(base.Child):

        @property
        def type(self):
            return self._xml.attrib['type']

        @property
        def mac_address(self):
            return self._xml.find('mac').attrib['address']

        @property
        def model(self):
            return self._xml.find('model').attrib['type']

        @property
        def network(self):
            source = self._xml.find('source')
            return source.attrib['network']

        def host(self):
            network = Network.find_by('name', self.network)
            for host in network.hosts:
                if host.mac_address == self.mac_address:
                    return host

        @property
        def ip_address(self):
            host = self.host()
            if host:
                return host.ip_address
