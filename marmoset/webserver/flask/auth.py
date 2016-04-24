from functools import wraps

from flask import request
from werkzeug.exceptions import Unauthorized

Username = 'admin'
Password = 'APgo1VANd6YPqP0ZaJ0OK9A7WHbXzFBqe6Nz8MU9rTxKv6gIZ26nIW1cfn4GbR36'


def required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        __authenticate()
        return f(*args, **kwargs)

    return decorated


def for_all_routes(app):
    app.before_request(__authenticate)
    app.config['HTTP_BASIC_AUTH_REALM'] = app.name
    return app


def __check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == Username and password == Password


def __authenticate():
    auth = request.authorization
    if not auth or not __check_auth(auth.username, auth.password):
        raise Unauthorized()
