from flask import request, make_response
from flask.ext.restful import Resource, url_for, abort

from ..installimage.installimage_config import InstallimageConfig
from ..installimage.req_argument_parser import ReqArgumentParser

parser = ReqArgumentParser()


class InstallimageCollection(Resource):
    def get(self):
        return [vars(c) for c in InstallimageConfig.all()]


class InstallimageObject(Resource):
    def get(self, mac):
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            return vars(installimage_config)
        else:
            abort(404)

    def post(self, mac):
        args = parser.parse_args(request)

        installimage_config = InstallimageConfig(mac)

        for key in args:
            installimage_config.add_or_set(key, args[key])

        installimage_config.create()

        location = url_for('installimageobject', _method='GET', mac=installimage_config.mac)
        return vars(installimage_config), 201, {'Location': location}

    def delete(self, mac):
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            installimage_config.remove()
            return '', 204
        else:
            abort(404)


class InstallimageConfigCommand(Resource):
    def get(self, mac):
        installimage_config = InstallimageConfig(mac)

        response = make_response(installimage_config.get_content())
        response.headers['content-type'] = 'text/plain'

        return response
