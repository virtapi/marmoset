"""File to handle all web interaction with installimage configurations"""
from flask import request, make_response
from flask.ext.restful import Resource, url_for, abort

from ..installimage.installimage_config import InstallimageConfig
from ..installimage.req_argument_parser import ReqArgumentParser

parser = ReqArgumentParser()


class InstallimageCollection(Resource):
    """Collection Class to deal with all installimage configurations"""

    def get(self):
        """Returns all current configurations"""
        return [vars(c) for c in InstallimageConfig.all()]


class InstallimageObject(Resource):
    """Class to handle a single installimage configuration"""

    def get(self, mac):
        """Returns a specific config based on the provided MAC"""
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            return vars(installimage_config)
        else:
            abort(404)

    def post(self, mac):
        """Creates or updates a config based on the provided MAC"""
        args = parser.parse_args(request)

        installimage_config = InstallimageConfig(mac)
        installimage_config.clear_variables()

        for key in args:
            for value in args.getlist(key):
                installimage_config.add_or_set(key, value)

        installimage_config.create()

        location = url_for(
            'installimageobject',
            _method='GET',
            mac=installimage_config.mac)
        return vars(installimage_config), 201, {'Location': location}

    def delete(self, mac):
        """Deletes a specific config based on the provided MAC"""
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            installimage_config.remove()
            return '', 204
        else:
            abort(404)


class InstallimageConfigCommand(Resource):
    """Class to do something?"""

    def get(self, mac):
        """Returns the configuration in a format suitable for the installimage"""
        installimage_config = InstallimageConfig(mac)

        response = make_response(installimage_config.get_content())
        response.headers['content-type'] = 'text/plain'

        return response
