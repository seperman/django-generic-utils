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



admin.site.register(Messages, MessagesAdmin)
admin.site.register(CeleryTasks, CeleryTasksAdmin)

