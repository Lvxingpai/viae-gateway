# coding=utf-8
# Create your views here.
import json
import uuid
from datetime import datetime, timedelta
import time
from settings import *

from django.http import HttpResponse, Http404
from djcelery import celery
import pymongo
from pymongo import MongoClient

client = MongoClient(MONGO_URL)


def send_to_mongo(task_data):
    """
    如果任务的eta太长,就存入mongoDB
    :param task_data:
    :return:
    """
    db = client.viae
    viae = db.viae
    post_id = viae.insert_one(task_data).inserted_id
    print(post_id, db.collection_names(include_system_collections=False))


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

        if countdown > COUNTDOWN_THRESHOLD:
            eta = datetime.now() + timedelta(seconds=countdown)
            data = {'task': task, 'id': str(uuid.uuid4()), 'args': args, 'kwargs': kwargs, 'eta': eta}
            send_to_mongo(data)
            data = {'taskId': '1111111111111111111111'}
            return HttpResponse(json.dumps(data), content_type="application/json")

        else:
            expires = task_data.get('expires')
            result = celery.send_task(task, serializer='json', args=args, kwargs=kwargs, countdown=countdown,
                                      expires=expires)
            data = {'taskId': result.task_id}
            return HttpResponse(json.dumps(data), content_type="application/json")
