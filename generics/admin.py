from django.contrib import admin

from generics.models import Messages

class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    verbose_name_plural = 'Messages'
    verbose_name = 'Message'

    filter_horizontal = ("users",)

    list_display = ("msg", "id",)

admin.site.register(Messages, MessagesAdmin)