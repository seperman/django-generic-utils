from django.core.cache import cache
import json
# from celery.result import AsyncResult
from django.core.exceptions import PermissionDenied
# from django.http import Http404
from django.http import HttpResponse
# from django.core.cache import cache
from django.utils import timezone

from generics.models import MessagesStatus

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#Trying to load celery
try:
    from celery.task.control import revoke
except ImportError:
    logger.info("celery was not found. Loading a mock version for Django Generics")
    def revoke(*args, **kwargs):
        return None


def task_api(request):
    """ A view to report the progress to the user """

    if not request.user.is_authenticated() or not request.user.is_active:
        raise PermissionDenied

    if request.method == "GET":
        task_id = request.GET.get('id', False)
        terminate = request.GET.get('terminate', False)
    elif request.method == "POST":
        task_id = request.POST.get('id', False)
        terminate = request.POST.get('terminate', False)
    else:
        task_id = False
        terminate = False

    if task_id:
        # job = AsyncResult(task_id)
        # job.result.state
        task_key = "celery-stat-%s" % task_id
        task_stat = cache.get(task_key)
        try:
            if task_stat['user_id'] != request.user.id:
                task_stat = None
        except TypeError:
            task_stat = None
    else:
        task_stat = None

    if task_stat and terminate=="1":
        logger.info("terminate: %s" % terminate)
        revoke(task_id, terminate=True)
        cache.delete(task_key)




    return HttpResponse(json.dumps(task_stat), mimetype='application/json')
# -*- coding: utf-8 -*-



def messages_api(request):
    """ A view to akhnowledge messages by users """

    if not request.user.is_authenticated() or not request.user.is_active:
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
        if action=="remove":
            result = MessagesStatus.objects.filter(message__pk=message_id, user=request.user).update(akhnowledge_date=timezone.now())
                # m.users.remove(request.user)
                # result = "Removed"
            # except MessagesStatus.DoesNotExist:
            #     raise Http404

    return HttpResponse(json.dumps(result), mimetype='application/json')

