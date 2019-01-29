"""Initial file for installstatus"""
from uuid import UUID
from marmoset import validation
from .installstatus import InstallStatus


def get_history(args):
    """Prints status update history related to installimage uuid"""
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        history = install_status.get_history()
        if history:
            for status in history:
                print('%s %s/%s %s %s' %
                      (status['date'], status['current_step'],
                       status['total_steps'], status['status_code'],
                       status['step_description']))
        else:
            print('No status updates for %s found.' % uuid)


def get_latest(args):
    """Prints latest status update related to installimage uuid"""
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        latest = install_status.get_latest_status()
        if latest is not None:
            print('%s %s/%s %s %s' %
                  (latest['date'], latest['current_step'],
                   latest['total_steps'], latest['status_code'],
                   latest['step_description']))
        else:
            print('No status updates for %s found.' % uuid)


def get_stats(args):
    """Prints some stats related to installimage uuid"""
    if is_uuid(args.uuid):
        uuid = str(UUID(args.uuid))
        install_status = InstallStatus(uuid)
        stats = install_status.get_stats()
        print_stats_order = ['uuid', 'start_date', 'end_date',
                             'installation_duration',
                             'status_updates', 'latest_status_code',
                             'latest_status_age']
        for stat in print_stats_order:
            print('%s: %s' % (stat, stats[stat]))


def is_uuid(uuid):
    """Check if provided string is a UUID"""
    if validation.is_uuid(uuid):
        return True
    else:
        print('Invalid uuid %s.' % uuid)
        return False
