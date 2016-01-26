from flask import request, make_response
from flask.ext.restful import reqparse, Resource, url_for, abort
from werkzeug.exceptions import NotFound
from .. import dhcp


class DhcpCollection(Resource):
    def get(self):
        return [vars(c) for c in dhcp.DhcpConfig]

    def post(self):
        pass


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