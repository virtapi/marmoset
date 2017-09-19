from functools import wraps

from flask import request, current_app
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


# we've to disable pep8 here because it detects uppercase chars in the method name
# pep8 compliance requires lowercase only function names, but thats the case
def __check_auth(username, password):  # nopep8
    """
    Check username/password combination

    This function is called to check if a username /
    password combination is valid.
    """
    return username == Username and password == Password


# we've to disable pep8 here because it detects uppercase chars in the method name
# pep8 compliance requires lowercase only function names, but thats the case
def __is_whitelist_endpoint(endpoint):  # nopep8
    """Check if a given endpoint is whitelisted in our configuration file"""
    whitelist_conf = current_app.config['AUTH_WHITELIST_ENDPOINT']
    if whitelist_conf is not None:
        whitelist = whitelist_conf.split(',')
        if endpoint in whitelist:
            return True
    return False


# we've to disable pep8 here because it detects uppercase chars in the method name
# pep8 compliance requires lowercase only function names, but thats the case
def __authenticate():  # nopep8
    auth = request.authorization
    if __is_whitelist_endpoint(request.endpoint):
        pass
    elif not auth or not __check_auth(auth.username, auth.password):
        raise Unauthorized()
