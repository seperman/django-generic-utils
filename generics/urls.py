from django.conf.urls import patterns, url #include,

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


urlpatterns = patterns(
    '',
    url(r'^task_api$', 'generics.views.task_api', name="task_api"),
    )

