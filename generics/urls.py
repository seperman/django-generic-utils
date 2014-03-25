from django.conf.urls import patterns, url #include,

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from celery.task.control import revoke
    
    urlpatterns = patterns(
        '',
        url(r'^task_api$', 'generics.views.task_api', name="task_api"),
        )
except ImportError:
    logger.error("Celery could NOT be imported", exc_info=True)

