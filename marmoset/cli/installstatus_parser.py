from .. import installstatus


def add_to(parser, name, **kwargs):
    command     = parser.add_parser(name, **kwargs)
    subcommands = command.add_subparsers(title='%s subcommands' % name)

    installstatus_history = subcommands.add_parser('history',
        help='lists all status updates for a uuid',
        aliases=['h', 'hist'])
    installstatus_history.add_argument('uuid',
        help='uuid to list status updates for')
    installstatus_history.set_defaults(func=installstatus.get_history)
    installstatus_stats = subcommands.add_parser('stats',
        help='list stats for a uuid',
        aliases=['s', 'stat'])
    installstatus_stats.add_argument('uuid',
        help='uuid to list status for')
    installstatus_stats.set_defaults(func=installstatus.get_stats)
    installstatus_latest = subcommands.add_parser('latest',
        help='show latest status for a uuid',
        aliases=['l'])
    installstatus_latest.add_argument('uuid',
        help='uuid to show latest status for')
    installstatus_latest.set_defaults(func=installstatus.get_latest)