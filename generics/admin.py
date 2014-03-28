from django.contrib import admin

from generics.models import Messages
from generics.forms import MessagesStatusForm

class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    verbose_name_plural = 'Messages'
    verbose_name = 'Message'

    form = MessagesStatusForm

    # filter_horizontal = ("users",)

    list_display = ("msg", "id",)

admin.site.register(Messages, MessagesAdmin)