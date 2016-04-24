from .. import virt


def add_to(parser, name, **kwargs):
    command = parser.add_parser(name,
                                description='Manage libvirt VMs which are defined on the host',
                                **kwargs)
    subcommands = command.add_subparsers(title='%s subcommands' % name)

    vm_create = subcommands.add_parser('create',
                                       help='Create a new VM.',
                                       aliases=['c', 'add'])
    vm_create.set_defaults(func=virt.create)
    vm_create.add_argument('-i', '--ip_address',
                           help='main IP address that is set with DHCP',
                           required=True)
    vm_create.add_argument('-u', '--user',
                           help='the user this VM is created for',
                           required=True)
    vm_create.add_argument('-n', '--name',
                           help='name of the vm (will be prefixed with user name)',
                           required=True)
    vm_create.add_argument('-s', '--size',
                           help='size of the disk in GB',
                           required=True)
    vm_create.add_argument('-m', '--memory',
                           help='memory for the VM in GB',
                           required=True)
    vm_create.add_argument('-c', '--cpu',
                           help='number of vcpus',
                           required=True)

    vm_list = subcommands.add_parser('list',
                                     help='list all currently defined VMs',
                                     aliases=['l'])
    vm_list.set_defaults(func=virt.list)

    vm_edit = subcommands.add_parser('edit',
                                     help='edit specs or configs of a VM',
                                     aliases=['e', 'ed'])
    vm_edit.set_defaults(func=virt.edit)
    vm_edit.add_argument('id', help='the libvirt ID of the VM')

    vm_remove = subcommands.add_parser('remove',
                                       help='remove a VM',
                                       aliases=['r', 'delete', 'del', 'd'])
    vm_remove.set_defaults(func=virt.remove)
    vm_remove.add_argument('id', help='the libvirt ID of the VM')
