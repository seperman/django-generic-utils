from django.core.cache import cache
import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
# from django.core.cache import cache

def task_status(request):
    """ A view to report the progress to the user """
    if not request.user.is_authenticated():
        raise PermissionDenied

    if request.method == "GET":
        task_id = request.GET.get('id', False)
    elif request.method == "POST":
        task_id = request.POST.get('id', False)
    else:
        task_id = False

    if task_id:
        # job = AsyncResult(task_id)
        # job.result.state
        task_stat = cache.get("celery-stat-%s" % task_id)
        if task_stat['user_id'] != request.user.id:
            task_stat = None
    else:
        task_stat = None


    return HttpResponse(json.dumps(task_stat), mimetype='application/json')

