# -*- coding: utf-8 -*-
# from django.core.cache import cache
from generics.cache import cache
import json
# from celery.result import AsyncResult
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from django.db import IntegrityError
from functools import wraps    # deals with decorats shpinx documentation

from generics import tasks
from generics.models import CeleryTasks, MessagesStatus
from generics.functions import decorator_with_args

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Trying to load celery
# try:
#     from celery.task.control import revoke
# except ImportError:
#     def revoke(*args, **kwargs):
#         return None


@decorator_with_args
def progressbarit(fn, task_key="", only_staff=True):
    @wraps(fn)
    def wrapped(*args, **kwargs):

        request = args[0]

        if only_staff:
            if not request.user.is_staff:
                raise PermissionDenied

        elif not request.user.is_active:
                raise PermissionDenied

        if task_key and CeleryTasks.objects.filter(key=task_key, status__in=["waiting", "active"]):

            json_data = json.dumps("Error: %s Task is already running" % task_key)
            return HttpResponse(json_data, content_type='application/json')

        try:
            task_id = fn(*args, **kwargs)
        except:
            json_data = json.dumps("Error: %s Task failed to run" % task_key)
            return HttpResponse(json_data, content_type='application/json')

        try:
            CeleryTasks.objects.create(task_id=task_id, user=request.user, key=task_key)
        except IntegrityError:
            # We don't want to have 2 tasks with the same ID
            logger.critical("There ware 2 tasks with the same ID. Trying to terminate the task.", exc_info=True)
            from celery.task.control import revoke
            revoke(task_id, terminate=True)
            raise

        json_data = json.dumps(task_id)

        return HttpResponse(json_data, content_type='application/json')

    return wrapped


def task_api(request):
    """ A view to report the progress to the user """

    if not request.user.is_active:
        raise PermissionDenied

    if request.method == "GET":
        task_id = request.GET.get('id', False)
        terminate = request.GET.get('terminate', False)
        msg_index_client = request.GET.get('msg_index_client', False)
    elif request.method == "POST":
        task_id = request.POST.get('id', False)
        terminate = request.POST.get('terminate', False)
        msg_index_client = request.POST.get('msg_index_client', False)
    else:
        task_id = False
        terminate = False
        msg_index_client = False

    if task_id:
        task_key = "celery-stat-%s" % task_id
        task_stat = cache.get(task_key)
        try:
            if task_stat['user_id'] != request.user.id:
                return HttpResponse('Unauthorized', status=401)
        except TypeError:
            return HttpResponse('Unauthorized', status=401)

        else:
            # logger.info("msg_index_client: %s   task_stat['msg_index']: %s" % (msg_index_client, task_stat['msg_index']))
            try:
                msg_index_client = int(msg_index_client)
            except:
                task_stat['msg_chunk'] = "Error in pointer index server call"
            else:
                if msg_index_client is not False and msg_index_client < task_stat['msg_index']:
                    whole_msg = cache.get("celery-%s-msg-all" % task_id)
                    task_stat['msg_chunk'] = whole_msg[msg_index_client:]
    else:
        task_stat = None

    if task_stat and terminate == "1":
        cache.set("celery-kill-%s" % task_id, True, 60 * 5)

    return HttpResponse(json.dumps(task_stat), content_type='application/json')


def messages_api(request):
    """ A view to akhnowledge messages by users """

    if not request.user.is_active:
        raise PermissionDenied

    if request.method == "GET":
        message_id = request.GET.get('id', False)
        action = request.GET.get('action', False)
    elif request.method == "POST":
        message_id = request.POST.get('id', False)
        action = request.POST.get('action', False)
    else:
        message_id = False

    result = None

    if message_id and action:
        if action == "remove":
            result = MessagesStatus.objects.filter(message__pk=message_id, user=request.user).update(akhnowledge_date=timezone.now())
            # m.users.remove(request.user)
            # result = "Removed"
            # except MessagesStatus.DoesNotExist:
            #     raise Http404

    return HttpResponse(json.dumps(result), content_type='application/json')


@progressbarit(only_staff=False)
def celery_test(request):
    """ Tests celery and celery progress bar """

    # you need to alwasy specify user_id with kwargs and NOT args

    job = tasks.test_progressbar.delay(user_id=request.user.id)

    return job.id


@decorator_with_args
def logined_json(fn, only_staff=True):
    @wraps(fn)
    def wrapped(*args, **kwargs):

        request = args[0]

        if only_staff:
            if not request.user.is_staff:
                raise PermissionDenied

        elif not request.user.is_active:
                raise PermissionDenied

        data = fn(*args, **kwargs)

        json_data = json.dumps(data)

        return HttpResponse(json_data, content_type='application/json')

    return wrapped




def proxy(request, server_prefix, only_staff=True, only_superuser=False, remove_num_chars_from_path=0):
    """
    Proxy to other servers. The point is to use Django's auth for proxying.
    Example:
    server_prefix="http://localhost:1234"
    remove_num_chars_from_path: Number of characters to be trimmed from the beginning of the request.path
    For example when using with celery flower, if we are sending /flower/... to this view, then we need to remove /flower
    This is usually done in Nginx but we have to do it manually here since we are sending all traffic through Django
    """
    if only_superuser:
        if not request.user.is_superuser:
            raise PermissionDenied
    elif only_staff:
        if not request.user.is_staff:
            raise PermissionDenied

    from django.http import HttpResponseNotAllowed
    import requests

    if request.method == 'GET':
        requestB = request.GET
        r = requests.get
    elif request.method == 'POST':
        requestB = request.POST
        r = requests.post
    else:
        return HttpResponseNotAllowed("Permitted methods are POST and GET")
    params = requestB.dict()
    # import ipdb
    # ipdb.set_trace()
    if remove_num_chars_from_path:
        url = server_prefix + request.path[remove_num_chars_from_path:]
    else:
        url = server_prefix + request.path
    try:
        response = r(url, params=params)
    except requests.exceptions.ConnectionError as e:
        if e.message.args[1][0] == 111:
            return HttpResponse('Connection is refused. Server must be off.', status=500)
    return HttpResponse(response.text, status=int(response.status_code), content_type=response.headers['content-type'])