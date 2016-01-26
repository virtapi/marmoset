from ldap3 import Server, Connection, ALL
from datetime import datetime


class ISCDhcpLdapConfig:
    def __init__(self, dhcp_config):
        self.dhcp_config = dhcp_config

    def save(self):
        server = Server('localhost', get_info=ALL)
        conn = Connection(server, 'cn=root,dc=example,dc=com', 'secret', auto_bind=True)

        entry_attributes = {'dhcpHWAddress': "ethernet %s" % self.dhcp_config.mac,
                            'dhcpStatements': ["fixed-address %s;" % self.dhcp_config.ip_address,
                                               "option subnet-mask %s;" % '255.255.255.0',
                                               "option routers %s;" % self.dhcp_config.gateway],
                            'dhcpComments': "date=%s dhcp-hostname=%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"), self.dhcp_config.dhcp_hostname)}

        conn.add("cn=%s,dc=example,dc=com" % self.dhcp_config.ip_address, 'dhcpHost', entry_attributes)

