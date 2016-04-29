from flask import Flask, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException


def response(code=200, headers={}, *args, **kwargs):
    # pylint: disable-msg=dangerous-default-value
    response = jsonify(*args, **kwargs)
    response.status_code = code
    response.headers.extend(headers)

    return response


def error(ex=None, code=500, headers={}):
    # pylint: disable-msg=dangerous-default-value
    code = ex.code if isinstance(ex, HTTPException) else code
    return response(code, headers, message=str(ex))


def app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    app = Flask(import_name, **kwargs)

    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = error

    return app
