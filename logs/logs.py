from .models import Log_file_info_by_log, Log_update_schedule_by_log
from utils import timemanager

class LogData(object):
    """Helper class for getting log related data from the Cassandra database. """

    @classmethod
    def get_log_update_info(cls, log_id, json_request=None):
        """
        Return log file and update info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        json_request -- if true, convert datetime to timestamp representation (bool).
        """
        log_update_info_data = []
        log_file_info_data = Log_file_info_by_log.get_log_file_info(log_id)
        log_update_schedule_data = Log_update_schedule_by_log.get_log_updates(log_id=log_id)
        log = {}
        if log_update_schedule_data:
            log_update_schedule_map = log_update_schedule_data[0]
            if json_request:
                tm = timemanager.TimeManager()
                log_last_update = tm.json_date_handler(log_update_schedule_map.get('log_last_update'))
                log_next_update = tm.json_date_handler(log_update_schedule_map.get('log_next_update'))
            else:
                log_last_update = log_update_schedule_map.get('log_last_update')
                log_next_update = log_update_schedule_map.get('log_next_update')
            log_update_interval_id = log_update_schedule_map.get('log_update_interval_id')
            log_update_interval = log_update_schedule_map.get('log_update_interval')
            log['log_last_update'] = log_last_update
            log['log_next_update'] = log_next_update
            log['log_update_interval_id'] = log_update_interval_id
            log['log_update_interval'] = log_update_interval
        if log_file_info_data:
            log_file_info_map = log_file_info_data[0]
            log_file_path = log_file_info_map.get('log_file_path')
            log_file_line_num = log_file_info_map.get('log_file_line_num')
            log['log_file_path'] = log_file_path
            log['log_file_line_num'] = log_file_line_num
        if log:
            log_update_info_data.append(log)
        return log_update_info_data

