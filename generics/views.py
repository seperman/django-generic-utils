from celery.result import AsyncResult
import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
# from django.core.cache import cache

def task_status(request):
    """ A view to report the progress to the user """
    if not request.user.is_authenticated():
        raise PermissionDenied

    if request.is_ajax():
        job_id = request.POST.get('id', False)
    elif request.method == "GET":
        job_id = request.GET.get('id', False)
    else:
        job_id = False

    if job_id:
        job = AsyncResult(job_id)

        state = job.state
        try:
            percent = job.progress_percent
        except AttributeError:
             
            if state == "STARTED":
                percent = 10
            elif state == "SUCCESS":
                percent = 100
            else:
                percent = 0
    
        data = {"progress_percent": percent, "state": state, }

    else:
        data = False


    return HttpResponse(json.dumps(data), mimetype='application/json')

