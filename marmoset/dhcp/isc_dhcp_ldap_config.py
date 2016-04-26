import re
from datetime import datetime

from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES

from marmoset import config as config_reader
from marmoset import validation

config = config_reader.load()


class ISCDhcpLdapConfig:

    def __init__(self, dhcp_config):
        self.dhcp_config = dhcp_config

    @staticmethod
    def __get_server_connection():
        server = Server(config['DHCPConfig'].get('ldap_server'),
                        port=int(config['DHCPConfig'].get('ldap_port')),
                        get_info=ALL)

        conn = Connection(server,
                          config['DHCPConfig'].get('ldap_bind_dn'),
                          config['DHCPConfig'].get('ldap_passwort'),
                          auto_bind=True)

        return conn

    def save(self):
        conn = self.__get_server_connection()

        dhcpStatements = [
            "fixed-address %s;" %
            self.dhcp_config.ip_address,
            "option subnet-mask %s;" %
            self.dhcp_config.networkmask]

        if self.dhcp_config.gateway is not None:
            dhcpStatements.append(
                "option routers %s;" %
                self.dhcp_config.gateway)

        for additional_statement in self.dhcp_config.additional_statements:
            dhcpStatements.append(
                "%s %s;" %
                (additional_statement,
                 self.dhcp_config.additional_statements[additional_statement]))

        entry_attributes = {
            'dhcpHWAddress': "ethernet %s" % self.dhcp_config.mac,
            'dhcpStatements': dhcpStatements,
            'dhcpComments': "date=%s dhcp-hostname=%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"),
                                                          self.dhcp_config.dhcp_hostname)}

        conn.add(
            "cn=%s,%s" %
            (self.dhcp_config.ip_address,
             config['DHCPConfig'].get('ldap_client_base_dn')),
            'dhcpHost',
            entry_attributes)

    @staticmethod
    def all():
        conn = ISCDhcpLdapConfig.__get_server_connection()

        entry_generator = conn.extend.standard.paged_search(
            search_base=config['DHCPConfig'].get('ldap_client_base_dn'),
            search_filter='(objectClass=dhcpHost)',
            search_scope=SUBTREE,
            attributes=['cn'],
            paged_size=5,
            generator=True)
        result = []
        for entry in entry_generator:
            result.append(
                ISCDhcpLdapConfig.get_by_ip(
                    entry['attributes']['cn'][0]))

        return result

    @staticmethod
    def __get_dn_by_ipv4(ip_address, multi=False):
        conn = ISCDhcpLdapConfig.__get_server_connection()
        conn.search(
            search_base=config['DHCPConfig'].get('ldap_client_base_dn'),
            search_filter='(cn=%s)' %
            ip_address,
            search_scope=SUBTREE,
            paged_size=5,
            attributes=[
                ALL_ATTRIBUTES,
                ALL_OPERATIONAL_ATTRIBUTES])

        entries = conn.response

        if entries is None or len(entries) == 0:
            if multi:
                return []
            return None

        if multi:
            dn_list = []
            for entry in entries:
                dn_list.append(entry['dn'])

            return dn_list

        return entries[0]['dn']

    @staticmethod
    def __get_dn_by_mac(mac_address, multi=False):
        conn = ISCDhcpLdapConfig.__get_server_connection()
        conn.search(
            search_base=config['DHCPConfig'].get('ldap_client_base_dn'),
            search_filter='(dhcpHWAddress=ethernet %s)' %
            mac_address,
            search_scope=SUBTREE,
            paged_size=5,
            attributes=[
                ALL_ATTRIBUTES,
                ALL_OPERATIONAL_ATTRIBUTES])

        entries = conn.response

        if entries is None or len(entries) == 0:
            if multi:
                return []
            return None

        if multi:
            dn_list = []
            for entry in entries:
                dn_list.append(entry['dn'])

            return dn_list

        return entries[0]['dn']

    @staticmethod
    def __get_dhcp_config(dn):
        from marmoset.dhcp import DhcpConfig

        conn = ISCDhcpLdapConfig.__get_server_connection()
        conn.search(search_base=dn,
                    search_filter='(objectClass=dhcpHost)',
                    search_scope=SUBTREE,
                    paged_size=5,
                    attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])

        entries = conn.response

        if len(entries) == 0:
            return None

        mac_option = str(entries[0]['attributes']['dhcpHWAddress'])

        regex_gateway = 'option routers\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        regex_networkmask = 'option subnet-mask\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)'

        mac = re.search('(%s)' % validation.MAC_REGEX, mac_option).group(0)
        ip = entries[0]['attributes']['cn'][0]

        gateway = None
        networkmask = None

        for dhcpStatement in entries[0]['attributes']['dhcpStatements']:
            if re.match(regex_gateway, dhcpStatement):
                gateway = re.search(regex_gateway, dhcpStatement).group(1)

            if re.match(regex_networkmask, dhcpStatement):
                networkmask = re.search(
                    regex_networkmask, dhcpStatement).group(1)

        dhcp_config = DhcpConfig(mac, ip, gateway, networkmask)

        additional_statements_str = config[
            'DHCPConfig'].get('additional_statements')
        additional_statements = additional_statements_str.split(',')

        for ldap_additional_statement in entries[
                0]['attributes']['dhcpStatements']:
            for additional_statement in additional_statements:
                regex_additional_statement = '%s\s+(.*);' % additional_statement

                if re.match(
                        regex_additional_statement,
                        ldap_additional_statement):
                    value = re.search(
                        regex_additional_statement,
                        ldap_additional_statement).group(1)
                    dhcp_config.add_additional_statement(
                        additional_statement, value)

        return dhcp_config

    @staticmethod
    def get_by_ip(ip_address):
        dn = ISCDhcpLdapConfig.__get_dn_by_ipv4(ip_address)

        if dn is None:
            return None

        return ISCDhcpLdapConfig.__get_dhcp_config(dn)

    @staticmethod
    def get_by_mac(mac_address):
        dn = ISCDhcpLdapConfig.__get_dn_by_mac(mac_address)

        if dn is None:
            return None

        return ISCDhcpLdapConfig.__get_dhcp_config(dn)

    @staticmethod
    def remove_by_ipv4(ipv4):
        dn_list = ISCDhcpLdapConfig.__get_dn_by_ipv4(ipv4, multi=True)

        for dn in dn_list:
            conn = ISCDhcpLdapConfig.__get_server_connection()
            conn.delete(dn)
            conn.unbind()

        return len(dn_list)

    @staticmethod
    def remove_by_mac(mac):
        dn_list = ISCDhcpLdapConfig.__get_dn_by_mac(mac, multi=True)

        for dn in dn_list:
            conn = ISCDhcpLdapConfig.__get_server_connection()
            conn.delete(dn)
            conn.unbind()

        return len(dn_list)
