from django.core.cache import cache
import json
# from celery.result import AsyncResult
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from celery.task.control import revoke
# from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



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
        task_stat = cache.get("celery-stat-%s" % task_id)
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




    return HttpResponse(json.dumps(task_stat), mimetype='application/json')
