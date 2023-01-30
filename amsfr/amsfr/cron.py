from django_cron import CronJobBase, Schedule
from django.core.management import call_command

class MyCronJob(CronJobBase):
    RUN_AT_TIMES = ['4:16', '4:17']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'amsfr.cron.MyCronJob'

    def do(self):
        call_command('dbbackup')