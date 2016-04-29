from flask.ext.restful import reqparse, Resource, abort

from .. import virt


def find_domain(uuid):
    domain = virt.Domain.find_by('uuid', uuid)
    if domain is None:
        abort(404)
    else:
        return domain


class VMCollection(Resource):

    def get(self):
        domains = virt.Domain.all()
        return [d.attributes() for d in domains]

    def post(self):
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

    def get(self, uuid):
        domain = find_domain(uuid)
        return domain.attributes()

    def put(self, uuid):
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
        try:
            virt.remove(dict(uuid=uuid))
            return '', 204
        except Exception as e:
            abort(422, message=str(e))


class VMCommand(Resource):

    def put(self, uuid):
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
