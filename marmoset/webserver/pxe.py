from flask.ext.restful import reqparse, Resource, url_for, abort

from .. import pxe

parser = reqparse.RequestParser()
parser.add_argument('ip_address', type=str)
parser.add_argument('password', type=str, default=None)
parser.add_argument('script', type=str, default=None)
parser.add_argument('uuid', type=str, default=None)
parser.add_argument('label', type=str, choices=pxe.Label.names(), default=pxe.Label.names()[0])


class PXECollection(Resource):
    def get(self):
        '''List all PXE entries.'''
        return [vars(c) for c in pxe.ClientConfig.all()]

    def post(self):
        """Add a PXE entry for the given ip_address. Password, uuid and script
        are optional parameters. Missing password or uuid will be auto generated
        by ClientConfig.
        """
        args = parser.parse_args()
        re = pxe.ClientConfig(args.ip_address, args.password, args.script, args.uuid)

        try:
            re.create(pxe.Label.find(args.label))
            location = url_for('pxeobject', _method='GET', ip_address=re.ip_address)
            return vars(re), 201, {'Location': location}
        except pxe.exceptions.InputError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))


class PXEObject(Resource):
    def get(self, ip_address):
        '''Lookup a PXE entry for the given ip_address.'''
        re = pxe.ClientConfig(ip_address)
        if re.exists():
            return vars(re)
        else:
            abort(404)

    def delete(self, ip_address):
        '''Remove a PXE entry for the given ip_address.'''
        re = pxe.ClientConfig(ip_address)
        if re.exists():
            re.remove()
            return '', 204
        else:
            abort(404)
