from django.conf.urls import patterns, url #include,

urlpatterns = patterns(
    '',
    url(r'^task_api$', 'generics.views.task_api', name="task_api"),
    )