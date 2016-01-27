from .isc_dhcp_ldap_config import ISCDhcpLdapConfig
from marmoset import validation
import socket


class DhcpConfig:
    def __init__(self, mac, ip_address, gateway=None, networkmask=None):
        self.mac = mac

        self.gateway = gateway
        self.networkmask = networkmask

        if validation.is_cidr(ip_address):
            self.ip_address = validation.get_ip_from_cidr(ip_address)

            if self.networkmask is None:
                self.networkmask = validation.get_nm_from_cidr(ip_address)

            if self.gateway is None:
                self.gateway = validation.get_gw_from_cidr(ip_address)
        else:
            self.ip_address = ip_address

        self.dhcp_hostname = socket.getfqdn()

        self.additional_statements = {}

    def add_additional_statement(self, key, value):
        self.additional_statements[key] = value

    def create_isc_ldap(self):
        isc_dhcp_config = ISCDhcpLdapConfig(self)
        isc_dhcp_config.save()
