# coding=utf-8
# Create your views here.
import json

from django.http import HttpResponse, Http404
from djcelery import celery


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
        expires = task_data.get('expires')
        result = celery.send_task(task, serializer='json', args=args, kwargs=kwargs, countdown=countdown, expires=expires)
        data = {'taskId': result.task_id}
        return HttpResponse(json.dumps(data), content_type="application/json")
