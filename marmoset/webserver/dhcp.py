from flask import request
from flask.ext.restful import reqparse, Resource, url_for, abort
from marmoset import dhcp

parser = None


def build_parameters(additional_statements):
    global parser

    parser = reqparse.RequestParser()
    parser.add_argument('mac', type=str, required=True)
    parser.add_argument('ip_address', type=str, required=True)
    parser.add_argument('gateway', type=str, required=False, default=None)
    parser.add_argument('networkmask', type=str, required=False, default=None)

    for additional_statement in additional_statements:
        parser.add_argument(additional_statement, type=str, required=False)


class DhcpCollection(Resource):
    def get(self):
        return [vars(c) for c in dhcp.DhcpConfig]

    def post(self):
        args = parser.parse_args()

        dhcp_config = dhcp.DhcpConfig(args.mac, args.ip_address, args.gateway, args.networkmask)

        for args_item in parser.args:
            if not args_item.required and args_item.name in args and args[args_item.name] is not None:
                dhcp_config.add_additional_statement(args_item.name, args[args_item.name])

        dhcp_config.create_isc_ldap()


class DhcpIpv4Object(Resource):
    def get(self, ipv4):
        dhcp_config = dhcp.DhcpConfig(ipv4=ipv4)

        if dhcp_config.exists():
            return vars(dhcp_config)
        else:
            abort(404)

    def put(self, ipv4):
        args = parser.parse_args(request)

        dhcp_config = dhcp.DhcpConfig(ipv4=ipv4)

        dhcp_config.create()

        location = url_for('dhcpipv4object', _method='GET', ipv4=dhcp_config.ipv4)
        return vars(dhcp_config), 201, {'Location': location}

    def delete(self, ipv4):
        dhcp_config = dhcp.DhcpConfig(ipv4=ipv4)

        if dhcp_config.exists():
            dhcp_config.remove()
            return '', 204
        else:
            abort(404)


class DhcpMacObject(Resource):
    def get(self, mac):
        dhcp_config = dhcp.DhcpConfig(mac=mac)

        if dhcp_config.exists():
            return vars(dhcp_config)
        else:
            abort(404)

    def put(self, mac):
        args = parser.parse_args(request)

        dhcp_config = dhcp.DhcpConfig(mac)

        dhcp_config.create()

        location = url_for('dhcpmacobject', _method='GET', mac=dhcp_config.mac)
        return vars(dhcp_config), 201, {'Location': location}

    def delete(self, mac):
        dhcp_config = dhcp.DhcpConfig(mac)

        if dhcp_config.exists():
            dhcp_config.remove()
            return '', 204
        else:
            abort(404)