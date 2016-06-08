"""ClI module for imagecatalog"""
from .. import imagecatalog


def add_to(parser, name, **kwargs):
    """Updates the CLI parser to support imagecatalog"""
    command = parser.add_parser(name, **kwargs)
    subcommands = command.add_subparsers(title='%s subcommands' % name)

    imagecatalog_list = subcommands.add_parser('list',
        help='lists all available images',
        aliases=['l', 'list'])
    imagecatalog_list.set_defaults(func=imagecatalog.list_all)
