from marmoset import config as config_reader
from .db_helper import DBHelper
import datetime

config = config_reader.load()


class InstallStatus:
    def __init__(self, uuid):
        self.uuid = uuid

    def get_latest_status(self):
        status = DBHelper.get_latest_status(self.uuid)
        return status

    def get_history(self):
        history = DBHelper.get_history(self.uuid)
        return history

    def get_stats(self):
        status_history = DBHelper.get_history(self.uuid)
        history_count = len(status_history)
        stats = {}
        if history_count >= 1:
            stats['start_date'] = status_history[0]['date']
            stats['end_date'] = status_history[-1]['date']
            stats['latest_status'] = status_history[-1]['status']
            datetime_start = self.convert_date(stats['start_date'])
            datetime_end = self.convert_date(stats['end_date'])
            duration = datetime_end - datetime_start
            duration = duration.total_seconds()
            stats['duration'] = str(duration)
            now = datetime.datetime.utcnow()
            now = now.replace(microsecond=0)
            latest_status_age = now - datetime_end
            latest_status_age = latest_status_age.total_seconds()
            stats['latest_status_age'] = str(latest_status_age)
        else:
            stats['start_date'] = None
            stats['end_date'] = None
            stats['last_status'] = None
            stats['duration'] = None
            stats['latest_status_age'] = None
        stats['status_updates'] = str(history_count)
        stats['uuid'] = self.uuid
        return stats

    @classmethod
    def convert_date(cls, date_string):
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return date