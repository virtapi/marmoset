"""File to handle all web interaction with installimage configurations."""
from flask import request, make_response
from flask_restful import Resource, url_for, abort

from ..installimage.installimage_config import InstallimageConfig
from ..installimage.req_argument_parser import ReqArgumentParser

parser = ReqArgumentParser()


class InstallimageCollection(Resource):
    """Collection Class to deal with all installimage configurations."""

    def get(self):
        """Return all current configurations."""
        return [vars(c) for c in InstallimageConfig.all()]


class InstallimageObject(Resource):
    """Class to handle a single installimage configuration."""

    def get(self, mac):
        """Return a specific config based on the provided MAC."""
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            return vars(installimage_config)
        abort(404)

    def post(self, mac):
        """Create or updates a config based on the provided MAC."""
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
        """Delete a specific config based on the provided MAC."""
        installimage_config = InstallimageConfig(mac)

        if installimage_config.exists():
            installimage_config.remove()
            return '', 204
        abort(404)


class InstallimageConfigCommand(Resource):
    """Class for handling installimage configs."""

    def get(self, mac):
        """Return the configuration as installimage format."""
        installimage_config = InstallimageConfig(mac)

        response = make_response(installimage_config.get_content())
        response.headers['content-type'] = 'text/plain'

        return response
