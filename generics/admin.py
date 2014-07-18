# -*- coding: utf-8 -*-
from django.contrib import admin

from generics.models import Messages, CeleryTasks #, MessagesStatus
from generics.forms import MessagesForm



class MessagesAdmin(admin.ModelAdmin):
    model = Messages

    form = MessagesForm

    # filter_horizontal = ("users",)

    list_display = ("msg_code", "id", "msg", )




class CeleryTasksAdmin(admin.ModelAdmin):
    model = CeleryTasks

    list_display = (
        'task_id',
        'creation_date',
        'start_date',
        'end_date',
        'duration',
        'status',
        'key',
        'user',)

    readonly_fields = list_display

    actions = ("double_check_state",)

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_add_permission(self, request):
        return False


    def get_actions(self, request):
        actions = super(CeleryTasksAdmin, self).get_actions(request)
        
        # if 'delete_selected' in actions:
        #     del actions['delete_selected']
        
        return actions


    def double_check_state(self, request, queryset):
        """removing from deleted item """

        from django.utils.safestring import mark_safe
        from django.core.cache import cache

        selected_tasks_stats = ""
        for task_obj in queryset:
            task_id = task_obj.task_id
            task_key = "celery-stat-%s" % task_id
            task_stat = cache.get(task_key)
            if task_stat:
                task_stat_formatted = ', '.join(['%s: %s' % (key, value) for (key, value) in task_stat.items()])
                selected_tasks_stats = "%s <p>---------</p><p>%s:</p> <p>%s</p>" % (selected_tasks_stats, task_id, task_stat_formatted)

        if selected_tasks_stats:
            selected_tasks_stats = "<p>The following recent tasks status could be retrieved: </p> %s" % selected_tasks_stats
        else:
            selected_tasks_stats = "<p>No recent task status could be retrieved</p>"


        self.message_user(request, mark_safe(selected_tasks_stats))
        

    double_check_state.short_description = "Retrieve the state of selected items!"


# from django.db.models.base import FieldDoesNotExist

admin.site.register(Messages, MessagesAdmin)
admin.site.register(CeleryTasks, CeleryTasksAdmin)

