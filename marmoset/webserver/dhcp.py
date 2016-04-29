from flask import request
from flask.ext.restful import Resource
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask.ext.restful import url_for

from marmoset import config as config_reader
from marmoset import dhcp
from marmoset import validation

config = config_reader.load()

additional_statements_str = config['DHCPConfig'].get('additional_statements')
additional_statements = additional_statements_str.split(',')

parser = reqparse.RequestParser()
parser.add_argument('mac', type=str, required=True)
parser.add_argument('ip_address', type=str, required=True)
parser.add_argument('gateway', type=str, required=False, default=None)
parser.add_argument('networkmask', type=str, required=False, default=None)

for additional_statement in additional_statements:
    parser.add_argument(additional_statement, type=str, required=False)


class DhcpCollection(Resource):

    def get(self):
        return [vars(c) for c in dhcp.DhcpConfig.all()]

    def post(self):
        args = parser.parse_args()

        if ((args.gateway is None and config['DHCPConfig'].getboolean(
                'force_gateway')) or args.networkmask is None) and not validation.is_cidr(args.ip_address):
            return {
                'message': 'missing parameter gateway and networkmask or give an ip address in CIDR notation'}, 406

        if not validation.is_ipv4(
                args.ip_address) and not validation.is_cidr(
                args.ip_address):
            return {'message': 'please provide a valid ipv4 address'}, 406

        if not validation.is_mac(args.mac):
            return {'message': 'please provide a valid mac address'}, 406

        if dhcp.DhcpConfig.exists_ipv4(args.ip_address):
            return {'message': 'dhcp record for ip address %s already exists' %
                    args.ip_address}, 409

        if dhcp.DhcpConfig.exists_mac(args.mac):
            return {'message': 'dhcp record for mac address %s already exists' %
                    args.mac}, 409

        dhcp_config = dhcp.DhcpConfig(
            args.mac,
            args.ip_address,
            args.gateway,
            args.networkmask)

        for args_item in parser.args:
            if not args_item.required and args_item.name in args and args[args_item.name] is not None and \
                    args_item.name is not 'gateway' and args_item.name is not 'networkmask':
                dhcp_config.add_additional_statement(
                    args_item.name, args[args_item.name])

        dhcp_config.create_isc_ldap()

        location = url_for(
            'dhcpipv4object',
            _method='GET',
            ipv4=dhcp_config.ip_address)
        return vars(dhcp_config), 201, {'Location': location}


class DhcpIpv4Object(Resource):

    def get(self, ipv4):
        if not validation.is_ipv4(ipv4):
            return {'message': 'please provide a valid ipv4 address'}, 406

        if not dhcp.DhcpConfig.exists_ipv4(ipv4):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_ip(ipv4)

        return vars(dhcp_config)

    def put(self, ipv4):
        args = parser.parse_args(request)

        if not validation.is_ipv4(ipv4):
            return {'message': 'please provide a valid ipv4 address'}, 406

        if not dhcp.DhcpConfig.exists_ipv4(ipv4):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_ip(ipv4)

        dhcp_config.set_settings(
            False,
            args.mac,
            args.ip_address,
            args.gateway,
            args.networkmask)

        for args_item in parser.args:
            if not args_item.required and args_item.name in args and args[args_item.name] is not None and \
                    args_item.name is not 'gateway' and args_item.name is not 'networkmask':
                dhcp_config.add_additional_statement(
                    args_item.name, args[args_item.name])

        dhcp_config.remove_by_ipv4()

        dhcp_config.create_isc_ldap()

        location = url_for(
            'dhcpipv4object',
            _method='GET',
            ipv4=dhcp_config.ip_address)
        return vars(dhcp_config), 201, {'Location': location}

    def delete(self, ipv4):
        if not validation.is_ipv4(ipv4):
            return {'message': 'please provide a valid ipv4 address'}, 406

        if not dhcp.DhcpConfig.exists_ipv4(ipv4):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_ip(ipv4)
        dhcp_config.remove_by_ipv4()

        return '', 204


class DhcpMacObject(Resource):

    def get(self, mac):
        if not validation.is_mac(mac):
            return {'message': 'please provide a valid mac address'}, 406

        if not dhcp.DhcpConfig.exists_mac(mac):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_mac(mac)

        return vars(dhcp_config)

    def put(self, mac):
        args = parser.parse_args(request)

        if not validation.is_mac(mac):
            return {'message': 'please provide a valid mac address'}, 406

        if not dhcp.DhcpConfig.exists_mac(mac):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_mac(mac)

        dhcp_config.set_settings(
            False,
            args.mac,
            args.ip_address,
            args.gateway,
            args.networkmask)

        for args_item in parser.args:
            if not args_item.required and args_item.name in args and args[args_item.name] is not None and \
                    args_item.name is not 'gateway' and args_item.name is not 'networkmask':
                dhcp_config.add_additional_statement(
                    args_item.name, args[args_item.name])

        dhcp_config.remove_by_mac()

        dhcp_config.create_isc_ldap()

        location = url_for('dhcpmacobject', _method='GET', mac=dhcp_config.mac)
        return vars(dhcp_config), 201, {'Location': location}

    def delete(self, mac):
        if not validation.is_mac(mac):
            return {'message': 'please provide a valid mac address'}, 406

        if not dhcp.DhcpConfig.exists_mac(mac):
            return abort(404)

        dhcp_config = dhcp.DhcpConfig.get_by_mac(mac)
        dhcp_config.remove_by_mac()

        return '', 204
