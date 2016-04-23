from .. import installimage


def add_to(parser, name, **kwargs):
    command = parser.add_parser(name, **kwargs)
    subcommands = command.add_subparsers(title='%s subcommands' % name)

    installimage_create = subcommands.add_parser('create',
                                                 help='Create a Installimage config for an MAC Address.',
                                                 aliases=['c', 'add'])
    installimage_create.add_argument('mac',
                                     help='MAC address to create Installimage config for')
    installimage_create.add_argument('--var',
                                     help='Add key value pair',
                                     nargs=2,
                                     action='append')
    installimage_create.set_defaults(func=installimage.create)
    installimage_list = subcommands.add_parser('list',
                                               help='list MAC addresses for all currently present Installimage configs',
                                               aliases=['l'])
    installimage_list.set_defaults(func=installimage.list)
    installimage_remove = subcommands.add_parser('remove',
                                                 help='remove a installimage config for a MAC address',
                                                 aliases=['r', 'delete', 'del', 'd'])
    installimage_remove.set_defaults(func=installimage.remove)
    installimage_remove.add_argument('mac', help='Mac address to remove installimage config for')
