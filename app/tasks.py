# coding=utf-8
from datetime import datetime, timedelta
from djcelery import celery
from settings import *
from database import client


@celery.task(name='viae.gateway.pollingTasks', bind=True, acks_late=True)
def polling_tasks(self):
    """
    以轮询的方式, 获得将要到期的任务
    :return:
    """
    coll = client.viae.ViaeTask
    tasks = coll.find({'eta': {'$lt': datetime.utcnow() + timedelta(seconds=TASK_ETA_THRESHOLD)}})
    for task in tasks:
        args = task.get('args', [])
        kwargs = task.get('kwargs', {})
        routing_key = task.get('routing_key')
        eta = task.get('eta')
        expires = task.get('expires')
        id = task.get('_id')
        task = task['task']
        celery.send_task(task, serializer='json', args=args, kwargs=kwargs, eta=eta,
                         routing_key=routing_key, expires=expires)
        coll.remove({'_id': id})

    polling_tasks.apply_async(routing_key='stashed_tasks', countdown=TASK_POLLING_INTERVAL)
