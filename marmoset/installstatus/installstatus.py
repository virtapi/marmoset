from marmoset import config as config_reader
from .db_helper import DBHelper
import datetime

config = config_reader.load()


class InstallStatus:

    """installimage status updates can be stored/retrieved by uuid"""

    def __init__(self, uuid):
        self.uuid = uuid

    def get_latest_status(self):
        """fetches latest status update for the installimage job

        :return: latest status update for the
        :rtpye: dict
        """
        status = DBHelper.get_latest_status(self.uuid)
        return status

    def get_history(self):
        """fetches all status updates related to the installimage job

        :return: a list including one dict per status update
        :rtype: list
        """
        history = DBHelper.get_history(self.uuid)
        return history

    def insert_status(self, status_code, step_description,
                      current_step, total_steps):
        """insert new status update for installimage job

        :param status_code: the status code of the current install step from
        installimage
        :param step_description: the description of the current install step
        :param current_step: the current step count from installimage
        :param total_steps: the total installation steps needed by installimage
        """
        DBHelper.insert_status(self.uuid, status_code, step_description,
                               current_step, total_steps)

    def get_stats(self):
        """generates some stats related to the installimage job

        :return: stats
        :rtype: dict
        """
        status_history = DBHelper.get_history(self.uuid)
        history_count = len(status_history)
        stats = {}
        if history_count >= 1:
            stats['start_date'] = status_history[0]['date']
            stats['end_date'] = status_history[-1]['date']
            stats['latest_status_code'] = status_history[-1]['status_code']
            stats['total_steps'] = status_history[-1]['total_steps']
            datetime_start = self.convert_date(stats['start_date'])
            datetime_end = self.convert_date(stats['end_date'])
            duration = datetime_end - datetime_start
            duration = duration.total_seconds()
            stats['installation_duration'] = int(duration)
            now = datetime.datetime.utcnow()
            now = now.replace(microsecond=0)
            latest_status_age = now - datetime_end
            stats['latest_status_age'] = int(latest_status_age.total_seconds())
        else:
            stats['total_steps'] = None
            stats['start_date'] = None
            stats['end_date'] = None
            stats['latest_status_code'] = None
            stats['installation_duration'] = None
            stats['latest_status_age'] = None
        stats['status_updates'] = history_count
        stats['uuid'] = self.uuid
        return stats

    def convert_date(self, date_string):
        """converts the date string from database to datetime object

        :param date_string:
        :return: datetime
        """
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return date
