from django.conf.urls.defaults import patterns, url #include,

urlpatterns = patterns(
    '',
    url(r'^task_status$', 'generics.views.task_status', name="task_status"),
    )