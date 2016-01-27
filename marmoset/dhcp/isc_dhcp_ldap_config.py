from ldap3 import Server, Connection, ALL
from datetime import datetime


class ISCDhcpLdapConfig:
    def __init__(self, dhcp_config):
        self.dhcp_config = dhcp_config

    def save(self):
        server = Server('localhost', get_info=ALL)
        conn = Connection(server, 'cn=root,dc=example,dc=com', 'secret', auto_bind=True)

        dhcpStatements = ["fixed-address %s;" % self.dhcp_config.ip_address,
                          "option subnet-mask %s;" % self.dhcp_config.networkmask,
                          "option routers %s;" % self.dhcp_config.gateway]

        for additional_statement in self.dhcp_config.additional_statements:
            dhcpStatements.append("%s %s;" % (additional_statement, self.dhcp_config.additional_statements[additional_statement]))

        entry_attributes = {'dhcpHWAddress': "ethernet %s" % self.dhcp_config.mac,
                            'dhcpStatements': dhcpStatements,
                            'dhcpComments': "date=%s dhcp-hostname=%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"), self.dhcp_config.dhcp_hostname)}

        conn.add("cn=%s,dc=example,dc=com" % self.dhcp_config.ip_address, 'dhcpHost', entry_attributes)

