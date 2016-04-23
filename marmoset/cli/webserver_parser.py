from .. import webserver


def add_to(parser, name, **kwargs):
    command = parser.add_parser(name, **kwargs)
    command.set_defaults(func=webserver.run)
