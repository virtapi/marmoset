"""initial file for providing a Flask based API."""
from flask import Flask, jsonify
# https://flask-restful.readthedocs.io/en/latest/quickstart.html
from flask_restful import Api
# from flask.ext import restful

from .flask import auth

API_VERSION = '1'
config = None


def jsonify_nl(*args, **kwargs):
    """Encode data to json."""
    resp = jsonify(*args, **kwargs)
    resp.set_data(resp.get_data() + b'\n')
    return resp


def app(config):
    """Setup the initial flask app."""
    auth.Username = config['Webserver'].get('Username')
    auth.Password = config['Webserver'].get('Password')

    app = Flask(config['Webserver'].get('BasicRealm'))
    auth.for_all_routes(app)
    app.config['SERVER_NAME'] = config['Webserver'].get('ServerName')
    app.config['AUTH_WHITELIST_ENDPOINT'] = \
        config['Webserver'].get('AuthWhitelistEndpoint')

    api = Api(
        app=app,
        prefix='/v{}'.format(API_VERSION)
    )

    if config['Modules'].getboolean('PXE'):
        from . import pxe
        api.add_resource(pxe.PXECollection, '/pxe')
        api.add_resource(pxe.PXEObject, '/pxe/<ip_address>')

    if config['Modules'].getboolean('VM'):
        from . import vm
        api.add_resource(vm.VMCollection, '/vm')
        api.add_resource(vm.VMObject, '/vm/<uuid>')
        api.add_resource(vm.VMCommand, '/vm/<uuid>/action')

    if config['Modules'].getboolean('INSTALLIMAGE'):
        from . import installimage
        api.add_resource(installimage.InstallimageCollection, '/installimage')
        api.add_resource(
            installimage.InstallimageObject,
            '/installimage/<mac>')
        api.add_resource(
            installimage.InstallimageConfigCommand,
            '/installimage/<mac>/config')

    if config['Modules'].getboolean('DHCP'):
        from . import dhcp

        api.add_resource(dhcp.DhcpCollection, '/dhcp')
        api.add_resource(dhcp.DhcpIpv4Object, '/dhcp/ipv4/<ipv4>')
        api.add_resource(dhcp.DhcpMacObject, '/dhcp/mac/<mac>')

    if config['Modules'].getboolean('INSTALLSTATUS'):
        from . import installstatus
        api.add_resource(installstatus.InstallStatusHistory,
                         '/installstatus/<uuid>/history')
        api.add_resource(installstatus.InstallStatusLatest,
                         '/installstatus/<uuid>/latest')
        api.add_resource(installstatus.InstallStatusReport,
                         '/installstatus/<uuid>')
        api.add_resource(installstatus.InstallStatusStats,
                         '/installstatus/<uuid>/stats')

    if config['Modules'].getboolean('IMAGECATALOG'):
        from . import imagecatalog
        api.add_resource(imagecatalog.ImageMetadataCollection,
                         '/imagecatalog')
        api.add_resource(imagecatalog.ImageMetadata,
                         '/imagecatalog/<image_file>')
        api.add_resource(imagecatalog.ImageSignature,
                         '/imagecatalog/<image_file>/signature')

    @app.errorhandler(404)
    def not_found(ex):
        """Generate a 404."""
        # pylint: disable-msg=unused-argument
        # pylint: disable-msg=unused-variable
        resp = jsonify_nl(message="Route not found.", status=404)
        resp.status_code = 404
        return resp

    @app.errorhandler(401)
    def unauthorized(ex):
        """Generate a 401"""
        # pylint: disable-msg=unused-argument
        # pylint: disable-msg=unused-variable
        resp = jsonify_nl(message="Unauthorized", status=401)
        resp.status_code = 401
        return resp

    return app


def run(args):
    """Run the flask app."""
    # pylint: disable-msg=unused-argument
    webserver = app(config)
    print(webserver.url_map)
    webserver.run(
        # pylint: disable-msg=unsubscriptable-object
        host=config['Webserver'].get('Host'),
        # pylint: disable-msg=unsubscriptable-object
        port=config['Webserver'].getint('Port'),
        # pylint: disable-msg=unsubscriptable-object
        debug=config['Webserver'].getboolean('Debug')
    )
