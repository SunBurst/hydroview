import threading
from django.conf import settings
from cassandra.cluster import Cluster
#from celery import shared_task
from celery.signals import worker_process_init, worker_process_shutdown

from hydroview.celeryconfig import app
from .management.commands import run_update

thread_local = threading.local()

@worker_process_init.connect
def open_cassandra_session(*args, **kwargs):
    cluster = Cluster([settings.DATABASES["cassandra"]["HOST"],], protocol_version=3)
    session = cluster.connect(settings.DATABASES["cassandra"]["NAME"])
    thread_local.cassandra_session = session

@worker_process_shutdown.connect
def close_cassandra_session(*args, **kwargs):
    session = thread_local.cassandra_session
    session.shutdown()
    thread_local.cassandra_session = None

@app.task
def init_run_update():
    print("init run update!")
    run_update.run_update()