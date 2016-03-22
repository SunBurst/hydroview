from django_cron import CronJobBase, Schedule

from logs.management.commands import run_update

class UpdateLogsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 # every 1 hour
    RUN_AT_TIMES = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00',
         '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'
        , '19:00', '20:00', '21:00', '22:00', '23:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)#run_every_mins=RUN_EVERY_MINS)
    code = 'hydroview.updatecronjob'    # a unique code

    def do(self):
        run_update.cron_job()