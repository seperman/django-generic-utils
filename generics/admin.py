# -*- coding: utf-8 -*-
from django.contrib import admin

from generics.models import Messages #, MessagesStatus
from generics.forms import MessagesForm



class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    verbose_name_plural = 'Messages'
    verbose_name = 'Message'

    form = MessagesForm

    # filter_horizontal = ("users",)

    list_display = ("msg_code", "id", "msg", )

admin.site.register(Messages, MessagesAdmin)