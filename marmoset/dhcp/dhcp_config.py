from .isc_dhcp_ldap_config import ISCDhcpLdapConfig


class DhcpConfig:
    def __init__(self, mac, ip_address, gateway, dhcp_hostname):
        self.mac = mac
        self.ip_address = ip_address
        self.gateway = gateway
        self.dhcp_hostname = dhcp_hostname

        self.additional_statements = {}

    def add_additional_statement(self, key, value):
        self.additional_statements[key] = value

    def create_isc_ldap(self):
        isc_dhcp_config = ISCDhcpLdapConfig(self)
        isc_dhcp_config.save()
