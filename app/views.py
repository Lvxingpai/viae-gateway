# coding=utf-8
# Create your views here.
import json
import uuid
from datetime import datetime, timedelta
from settings import *

from django.http import HttpResponse, Http404
from djcelery import celery
from pymongo import MongoClient

client = MongoClient(MONGO_URL)


def send_to_mongo(task_data):
    """
    如果任务的eta太长,就存入mongoDB
    :param task_data:
    :return:
    """
    client.viae.ViaeTask.insert_one(task_data)


def tasks(request):
    """
    POST /tasks/
    在Celery中创建一条任务
    :param request:
    :return:
    """
    if request.method != 'POST':
        return Http404()
    else:
        task_data = json.loads(request.body)
        task = task_data['task']
        args = task_data.get('args', [])
        kwargs = task_data.get('kwargs', {})
        countdown = task_data.get('countdown')

        if countdown > TASK_COUNTDOWN_THRESHOLD:
            eta = datetime.utcnow() + timedelta(seconds=countdown)
            id = str(uuid.uuid4())
            data = {'task': task, '_id': id, 'args': args, 'kwargs': kwargs, 'eta': eta}
            send_to_mongo(data)
            data = {
                "taskId": id,
                "status": "stashed"
            }
            return HttpResponse(json.dumps(data), content_type="application/json")

        else:
            expires = task_data.get('expires')
            result = celery.send_task(task, serializer='json', args=args, kwargs=kwargs, countdown=countdown,
                                      expires=expires)
            data = {
                'taskId': result.task_id,
                'status': "pending"
            }
            return HttpResponse(json.dumps(data), content_type="application/json")
