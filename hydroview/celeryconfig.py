#!/usr/bin/env python
from __future__ import absolute_import

import os

from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from django.conf import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery('hydroview')  # Name of the folder where this file is

# Using a string here means the worker will not have to
# pickle the object when using Windows.
#app.config_from_object('django.conf:settings')
app.config_from_object('hydroview.celeryconfig')

# This allows you to load tasks from app/tasks.py files, they are
# autodiscovered. Check @shared_app decorator to do that.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERYBEAT_SCHEDULE = {
    # Executes every 15 minutes
    'update-every-15-min': {
        'task': 'logs.tasks.init_run_update',
        'schedule': crontab(minute='*/1'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))