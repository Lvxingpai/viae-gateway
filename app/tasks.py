from datetime import datetime, timedelta
from djcelery import celery
from settings import *
from pymongo import MongoClient

client = MongoClient(MONGO_URL)


@celery.task(name='viae.gateway.stashTask', bind=True, acks_late=True)
def mongo_to_celery():
    coll = client.viae.ViaeTask
    tasks = coll.find({'eta': {'$lt': datetime.now() + timedelta(seconds=TASK_ETA_THRESHOLD)}})
    for task in tasks:
        args = task.get('args', [])
        kwargs = task.get('kwargs', {})
        eta = task.get('eta')
        expires = task.get('expires')
        id = task.get('_id')
        task = task['task']
        celery.send_task(task, serializer='json', args=args, kwargs=kwargs, eta=eta,
                         expires=expires)
        coll.remove({'_id': id})
    mongo_to_celery.apply_async(countdown=TASK_POLLING_INTERVAL)
