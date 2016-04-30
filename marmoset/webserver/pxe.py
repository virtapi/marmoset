"""File to handle all web interaction with PXE records"""
from flask.ext.restful import reqparse, Resource, url_for, abort

from .. import pxe

parser = reqparse.RequestParser()
parser.add_argument('ip_address', type=str)
parser.add_argument('password', type=str, default=None)
parser.add_argument('script', type=str, default=None)
parser.add_argument('uuid', type=str, default=None)
parser.add_argument(
    'label',
    type=str,
    choices=pxe.Label.names(),
    default=pxe.Label.names()[0])


class PXECollection(Resource):
    """Collection class to deal with PXE records"""

    def get(self):
        """List all PXE entries."""
        return [vars(c) for c in pxe.ClientConfig.all()]

    def post(self):
        """
        Accepts a new PXE entry

        Add a PXE entry for the given ip_address. Password, uuid and script
        are optional parameters. Missing password or uuid will be auto generated
        by ClientConfig.
        """
        args = parser.parse_args()
        client_config = pxe.ClientConfig(
            args.ip_address,
            args.password,
            args.script,
            args.uuid)

        try:
            client_config.create(pxe.Label.find(args.label))
            location = url_for(
                'pxeobject',
                _method='GET',
                ip_address=client_config.ip_address)
            return vars(client_config), 201, {'Location': location}
        except pxe.exceptions.InputError as exception:
            abort(400, message=str(exception))
        except Exception as exception:
            abort(500, message=str(exception))


class PXEObject(Resource):
    """Class to handle a single PXE record"""

    def get(self, ip_address):
        """Lookup a PXE entry for the given ip_address."""
        client_config = pxe.ClientConfig(ip_address)
        if client_config.exists():
            return vars(client_config)
        else:
            abort(404)

    def delete(self, ip_address):
        """Remove a PXE entry for the given ip_address."""
        client_config = pxe.ClientConfig(ip_address)
        if client_config.exists():
            client_config.remove()
            return '', 204
        else:
            abort(404)
