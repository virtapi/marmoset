"""ClI module for installimage status updates"""
from .. import installstatus


def add_to(parser, name, **kwargs):
    """
    Updates the CLI parser to support installimage status updates and stats.

    supports a lot of information based on a UUID. For example a list of
    all status updates a UUID got, the last update it got or some stats for it.
    """
    command = parser.add_parser(name, **kwargs)
    subcommands = command.add_subparsers(title='%s subcommands' % name)

    installstatus_history = subcommands.add_parser('history',
        help='lists all status updates for a uuid',  # nopep8
        aliases=['h', 'hist'])
    installstatus_history.add_argument('uuid',
        help='uuid to list status updates for')  # nopep8
    installstatus_history.set_defaults(func=installstatus.get_history)
    installstatus_stats = subcommands.add_parser('stats',
        help='list stats for a uuid',  # nopep8
        aliases=['s', 'stat'])
    installstatus_stats.add_argument('uuid',
        help='uuid to list status for')  # nopep8
    installstatus_stats.set_defaults(func=installstatus.get_stats)
    installstatus_latest = subcommands.add_parser('latest',
        help='show latest status for a uuid',  # nopep8
        aliases=['l'])
    installstatus_latest.add_argument('uuid',
        help='uuid to show latest status for')  # nopep8
    installstatus_latest.set_defaults(func=installstatus.get_latest)
