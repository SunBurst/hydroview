import os
import threading
from django.conf import settings
from cassandra.cluster import Cluster
from celery import Celery
from celery import task
from celery.signals import worker_process_init, worker_process_shutdown

thread_local = threading.local()

celery = Celery('tasks', broker="amqp://myuser:mypassword@localhost:5672/myvhost") #!

os.environ['DJANGO_SETTINGS_MODULE'] = "hydroview.settings"

@worker_process_init.connect
def open_cassandra_session(*args, **kwargs):
    cluster = Cluster([settings.DATABASES["cassandra"]["HOST"],], protocol_version=3)
    session = cluster.connect(settings.DATABASES["cassandra"]["NAME"])
    thread_local.cassandra_session = session

@worker_process_shutdown.connect
def close_cassandra_session(*args,**kwargs):
    session = thread_local.cassandra_session
    session.shutdown()
    thread_local.cassandra_session = None

@task()
def test():
    print("test")