from .installstatus import InstallStatus
from marmoset import validation
from uuid import UUID


def get_history(args):
    """
    prints status update history related to installimage uuid

    """
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        history = install_status.get_history()
        if history:
            for status in history:
                print('%s: %s' % (status['date'], status['status']))
        else:
            print('No status updates for %s found.' % uuid)


def get_latest(args):
    """
    prints latest status update related to installimage uuid

    """
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        latest = install_status.get_latest_status()
        if latest is not None:
            print('%s: %s' % (latest['date'], latest['status']))
        else:
            print('No status updates for %s found.' % uuid)


def get_stats(args):
    """
    prints some stats related to installimage uuid

    """
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        stats = install_status.get_stats()
        print_stats_order = ['uuid', 'start_date', 'end_date', 'duration',
                             'status_updates', 'latest_status',
                             'latest_status_age']
        for stat in print_stats_order:
            print('%s: %s' % (stat, stats[stat]))


def is_uuid(uuid):
    if validation.is_uuid(uuid):
        return True
    else:
        print('Invalid uuid %s.' % uuid)
        return False