from django.conf.urls.defaults import patterns, url #include,

urlpatterns = patterns(
    '',
    url(r'^task_api$', 'generics.views.task_api', name="task_api"),
    )