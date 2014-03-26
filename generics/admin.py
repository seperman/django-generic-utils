from django.contrib import admin

from generics.models import Messages

class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    verbose_name_plural = 'Messages'
    verbose_name = 'Message'

    list_display = ("id", "msg", )

admin.site.register(Messages, MessagesAdmin)