"""initial file for providing a Flask based API"""
from flask import Flask, jsonify
from flask.ext import restful

from .flask import auth

API_VERSION = '1'
config = None


def jsonify_nl(*args, **kwargs):
    resp = jsonify(*args, **kwargs)
    resp.set_data(resp.get_data() + b'\n')
    return resp


def app(config):
    auth.Username = config['Webserver'].get('Username')
    auth.Password = config['Webserver'].get('Password')

    app = Flask(config['Webserver'].get('BasicRealm'))
    auth.for_all_routes(app)
    app.config['SERVER_NAME'] = config['Webserver'].get('ServerName')

    api = restful.Api(
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

    @app.errorhandler(404)
    def not_found(ex):
        resp = jsonify_nl(message="Route not found.", status=404)
        resp.status_code = 404
        return resp

    @app.errorhandler(401)
    def not_found(ex):
        resp = jsonify_nl(message="Unauthorized", status=401)
        resp.status_code = 401
        return resp

    return app


def run(args):
    global config
    webserver = app(config)
    print(webserver.url_map)
    webserver.run(
        host=config['Webserver'].get('Host'),
        port=config['Webserver'].getint('Port'),
        debug=config['Webserver'].getboolean('Debug')
    )
