"""helper fill with several validation functions"""
import ipaddress
import re
from uuid import UUID

MAC_REGEX = "([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}"


def is_mac(mac):
    """Returns True if param is a valid MAC"""
    return True if re.match("^%s$" % MAC_REGEX, mac) else False


def is_ipv4(ip):
    """Returns True if param is a valid IPv4 address"""
    try:
        ipaddress.IPv4Address(ip)
    except:
        return False
    return True


def is_ipv6(ipaddr):
    """Returns True if param is a valid IPv6 address"""
    try:
        ipaddress.IPv6Address(ipaddr)
    except:
        return False
    return True


def is_cidr(cidr):
    """Returns True if param is a valid IPv4 CIDR"""
    try:
        if "/" not in cidr:
            return False

        ipaddress.IPv4Interface(cidr)
    except:
        return False
    return True


def is_uuid(uuid):
    """Returns True if param is a valid UUID"""
    try:
        UUID(uuid)
    except:
        return False
    return True


def get_cidr(cidr):
    """Returns a hash with parsed CIDR, containing IP, Netmask, Gateway"""
    interface = ipaddress.IPv4Interface(cidr)
    gateway = list(interface.network.hosts())[0]
    return {'ip': str(interface.ip),
            'nm': str(interface.netmask),
            'gw': str(gateway)}


def get_ip_from_cidr(cidr):
    """Returns the IP from a CIDR"""
    data = get_cidr(cidr)
    return data['ip']


def get_nm_from_cidr(cidr):
    """Returns the netmask from a CIDR"""
    data = get_cidr(cidr)
    return data['nm']


def get_gw_from_cidr(cidr):
    """Returns the gateway from a CIDR"""
    data = get_cidr(cidr)
    return data['gw']
