from qcs.models import Log_quality_control_schedule_by_log, Quality_control_level_info_by_log
from utils.timemanager import TimeManager

class QCData(object):
    """Helper class for getting quality control related data from the Cassandra database. """

    @classmethod
    def get_log_qc_info(cls, log_id, json_request=None):
        """
        Return log qc info and schedule or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        json_request -- if true, convert datetime to timestamp representation (bool).
        """
        log_qc_info_data = []
        log_qc_info_query = Quality_control_level_info_by_log.objects.filter(log_id=log_id)
        for row in log_qc_info_query:
            log_qc_level = row.qc_level
            log_qc_schedule_query = Log_quality_control_schedule_by_log.objects.filter(
                log_id=log_id, qc_level=log_qc_level
            )
            try:
                log_qc_schedule_query = log_qc_schedule_query[0]
            except IndexError:
                print("Index error!")
            if json_request:
                tm = TimeManager()
                log_last_qc = tm.json_date_handler(log_qc_schedule_query.log_last_quality_control)
                log_next_qc = tm.json_date_handler(log_qc_schedule_query.log_next_quality_control)
            else:
                log_last_qc = log_qc_schedule_query.log_last_quality_control
                log_next_qc = log_qc_schedule_query.log_next_quality_control
            log = {
                'log_qc_level' : log_qc_level,
                'log_qc_name' : row.qc_name,
                'log_qc_interval' : log_qc_schedule_query.get('log_qc_interval'),
                'log_last_quality_control' : log_last_qc,
                'log_next_quality_control' : log_next_qc,
                'log_qc_replacement_value' : row.qc_replacement_value
            }
            log_qc_info_data.append(log)
        return log_qc_info_data

