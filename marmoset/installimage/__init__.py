"""Initial file for dealing with installimage configs."""
from .installimage_config import InstallimageConfig


def create(args):
    """Get the installimage options and passed them further to store them."""
    install_config = InstallimageConfig(args.mac)

    for var in args.var:
        install_config.add_or_set(var[0], var[1])

    install_config.create()

    msg = 'Created %s with following Options:\n%s' % (
        install_config.file_path(), install_config.get_content())

    print(msg)


def dolist(args):
    """Print all configs"""
    # pylint: disable-msg=unused-argument
    for install_config in InstallimageConfig.all():
        print('%s' % install_config.mac)


def remove(args):
    """Remove a certain entry."""
    install_config = InstallimageConfig(args.mac)
    if install_config.remove():
        print('Removed', install_config.file_path())
    else:
        print('No entry found for', install_config.mac)
