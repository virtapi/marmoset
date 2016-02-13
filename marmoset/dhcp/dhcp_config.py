from .isc_dhcp_ldap_config import ISCDhcpLdapConfig
from marmoset import validation
from marmoset import config as config_reader

config = config_reader.load()


class DhcpConfig:
    def __init__(self, mac, ip_address, gateway=None, networkmask=None):
        self.additional_statements = {}

        self.mac = None
        self.ip_address = None
        self.gateway = None
        self.networkmask = None
        self.dhcp_hostname = None

        self.set_settings(True, mac, ip_address, gateway, networkmask)

    def set_settings(self, allow_none_value_for_not_required_parameter=False, mac=None, ip_address=None,
                     gateway=None, networkmask=None):
        self.mac = mac

        if gateway is not None or allow_none_value_for_not_required_parameter:
            self.gateway = gateway

        if networkmask is not None or allow_none_value_for_not_required_parameter:
            self.networkmask = networkmask

        if validation.is_cidr(ip_address):
            self.ip_address = validation.get_ip_from_cidr(ip_address)

            if self.networkmask is None:
                self.networkmask = validation.get_nm_from_cidr(ip_address)

            if self.gateway is None:
                self.gateway = validation.get_gw_from_cidr(ip_address)
        else:
            self.ip_address = ip_address

        self.dhcp_hostname = config['Common'].get('FQDN')

    def add_additional_statement(self, key, value):
        self.additional_statements[key] = value

    def create_isc_ldap(self):
        isc_dhcp_config = ISCDhcpLdapConfig(self)
        isc_dhcp_config.save()

    def remove_by_ipv4(self):
        return ISCDhcpLdapConfig.remove_by_ipv4(self.ip_address) > 0

    def remove_by_mac(self):
        return ISCDhcpLdapConfig.remove_by_mac(self.mac) > 0

    def remove_all(self):
        ipv4_removed_count = ISCDhcpLdapConfig.remove_by_ipv4(self.ip_address)
        mac_removed_count = ISCDhcpLdapConfig.remove_by_mac(self.mac)

        return (ipv4_removed_count + mac_removed_count) > 0

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
