from flask.ext.restful import reqparse, Resource, abort

from .. import virt


def find_domain(uuid):
    """Searches for a given domain based on the provided UUID"""
    domain = virt.Domain.find_by('uuid', uuid)
    if domain is None:
        abort(404)
    else:
        return domain


class VMCollection(Resource):
    """Collection class to deal with all virtual machines"""
    def get(self):
        """returns all domains"""
        domains = virt.Domain.all()
        return [d.attributes() for d in domains]

    def post(self):
        """creates a new virtual machine"""
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('memory', type=str, required=True)
        parser.add_argument('cpu', type=int, default=1)
        parser.add_argument('disk', type=str, required=True)
        parser.add_argument('ip_address', type=str, required=True)
        parser.add_argument('password', type=str, default=None)
        args = parser.parse_args()
        try:
            domain = virt.create(args)
            return domain.attributes()
        except Exception as e:
            abort(422, message=str(e))


class VMObject(Resource):
    """Class to handle a single virtual machine"""
    def get(self, uuid):
        """returns a single domain based on the UUID"""
        domain = find_domain(uuid)
        return domain.attributes()

    def put(self, uuid):
        """Updates a domain based on the provided UUID"""
        domain = find_domain(uuid)
        parser = reqparse.RequestParser()
        parser.add_argument('memory', type=str, store_missing=False)
        parser.add_argument('cpu', type=int, store_missing=False)
        parser.add_argument('password', type=str, store_missing=False)
        args = parser.parse_args()
        try:
            domain = virt.edit(domain, args)
            return domain.attributes()
        except Exception as e:
            abort(422, message=str(e))

    def delete(self, uuid):
        """Deletes a domain based on the provided UUID"""
        try:
            virt.remove(dict(uuid=uuid))
            return '', 204
        except Exception as e:
            abort(422, message=str(e))


class VMCommand(Resource):
    """Class to send libvirt commands to a domain"""
    def put(self, uuid):
        """Sends the provided command to a given UUID"""
        parser = reqparse.RequestParser()
        parser.add_argument('command', type=str, required=True,
                            choices=['start', 'stop', 'shutdown', 'reset'])
        parser.add_argument('params', type=str, action='append', default=[])
        args = parser.parse_args()
        domain = find_domain(uuid)
        try:
            res = getattr(domain, args.command)(*args.params)
            return ('', 204) if not res else (res, 200)
        except Exception as e:
            abort(422, message=str(e))
