"""helper fill with several validation functions."""
import ipaddress
import re
from uuid import UUID

MAC_REGEX = "([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}"


def is_mac(mac):
    """Return True if param is a valid MAC."""
    re.match("^%s$" % MAC_REGEX, mac)


def is_ipv4(ipaddr):
    """Return True if param is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ipaddr)
    except ipaddress.AddressValueError:
        return False
    return True


def is_ipv6(ipaddr):
    """Return True if param is a valid IPv6 address."""
    try:
        ipaddress.IPv6Address(ipaddr)
    except ipaddress.AddressValueError:
        return False
    return True


def is_cidr(cidr):
    """Return True if param is a valid IPv4 CIDR."""
    try:
        if "/" not in cidr:
            return False

        ipaddress.IPv4Interface(cidr)
    except ipaddress.AddressValueError:
        return False
    return True


def is_uuid(uuid):
    """Return True if param is a valid UUID."""
    try:
        UUID(uuid)
    except Exception:
        return False
    return True


def get_cidr(cidr):
    """Return a hash with parsed CIDR, containing IP, Netmask, Gateway."""
    interface = ipaddress.IPv4Interface(cidr)
    gateway = list(interface.network.hosts())[0]
    return {'ip': str(interface.ip),
            'nm': str(interface.netmask),
            'gw': str(gateway)}


def get_ip_from_cidr(cidr):
    """Return the IP from a CIDR."""
    data = get_cidr(cidr)
    return data['ip']


def get_nm_from_cidr(cidr):
    """Return the netmask from a CIDR."""
    data = get_cidr(cidr)
    return data['nm']


def get_gw_from_cidr(cidr):
    """Return the gateway from a CIDR."""
    data = get_cidr(cidr)
    return data['gw']
