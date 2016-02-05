from .isc_dhcp_ldap_config import ISCDhcpLdapConfig
from marmoset import validation
import socket


class DhcpConfig:
    def __init__(self, mac, ip_address, gateway=None, networkmask=None):
        self.additional_statements = {}

        self.mac = None
        self.ip_address = None
        self.gateway = None
        self.networkmask = None
        self.dhcp_hostname = None

        self.set_settings(True, mac, ip_address, gateway, networkmask)

    def set_settings(self, set_not_required_if_none=False, mac=None, ip_address=None, gateway=None, networkmask=None):
        self.mac = mac

        if gateway is not None or set_not_required_if_none:
            self.gateway = gateway

        if networkmask is not None or set_not_required_if_none:
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

    def add_additional_statement(self, key, value):
        self.additional_statements[key] = value

    def create_isc_ldap(self):
        isc_dhcp_config = ISCDhcpLdapConfig(self)
        isc_dhcp_config.save()

    def remove(self):
        return ISCDhcpLdapConfig.remove(self.ip_address) is not None

    @staticmethod
    def all():
        return ISCDhcpLdapConfig.all()

    @staticmethod
    def get_by_ip(ip_address):
        return ISCDhcpLdapConfig.get_by_ip(ip_address)

    @staticmethod
    def get_by_mac(mac):
        return ISCDhcpLdapConfig.get_by_mac(mac)

    @staticmethod
    def exists_ipv4(ip_address):
        return ISCDhcpLdapConfig.get_by_ip(ip_address) is not None

    @staticmethod
    def exists_mac(mac_address):
        return ISCDhcpLdapConfig.get_by_mac(mac_address) is not None
