from . import base


class Network(base.Parent):
    DEFAULT = 'default'

    _func = dict(
        all='listAllNetworks',
        uuid='networkLookupByUUIDString',
        id='networkLookupByID',
        name='networkLookupByName'
    )

    @property
    def uuid(self):
        return self._resource.UUIDString()

    @property
    def name(self):
        return self._resource.name()

    @property
    def bridge(self):
        return self._resource.bridgeName()

    @property
    def hosts(self):
        hosts = self.get_xml().findall('./ip/dhcp/host')
        return [Network.Host(host, self) for host in hosts]

    def get_host(self, mac_address):
        xpath = "./ip/dhcp/host[@mac='{}']".format(mac_address)
        return self.get_xml().find(xpath)

    def knows_host(self, mac_address):
        return False if self.get_host(mac_address) is None else True

    def knows_ip_address(self, ip_address):
        xpath = "./ip/dhcp/host[@ip='{}']".format(ip_address)
        host = self.get_xml().find(xpath)
        return False if host is None else True

    def add_host(self, mac_address, ip_address, name=''):
        attrs = {k: v for k, v in locals().items() if k != 'self'}
        self._update_hosts('add', **attrs)
        return Network.Host(self.get_host(mac_address), self)

    def _update_hosts(self, command, **kwargs):
        """https://www.libvirt.org/html/libvirt-libvirt-network.html"""
        commands = dict(add=3, delete=2, modify=1)
        xml = Network.Host.XML.format(**kwargs)
        self._resource.update(commands[command], 4, -1, xml)

    class Host(base.Child):

        XML = "<host mac='{mac_address}' name='{name}' ip='{ip_address}'/>"

        @property
        def mac_address(self):
            return self._xml.attrib.get('mac')

        @property
        def name(self):
            return self._xml.attrib.get('name')

        @property
        def ip_address(self):
            return self._xml.attrib.get('ip')

        def update(self, ip_address=None, name=None):
            attrs = self.attributes()
            for key in ['ip_address', 'name']:
                if locals()[key] is not None:
                    attrs[key] = locals()[key]
            self._parent._update_hosts('modify', **attrs)
            self._xml = self._parent.get_host(attrs['mac_address'])

        def delete(self):
            self._parent._update_hosts('delete', **self.attributes())
