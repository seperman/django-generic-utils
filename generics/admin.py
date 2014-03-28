from django.contrib import admin

from generics.models import Messages, MessagesStatus
from generics.forms import MessagesForm



class MessagesAdmin(admin.ModelAdmin):
    model = Messages
    verbose_name_plural = 'Messages'
    verbose_name = 'Message'

    form = MessagesForm

    # filter_horizontal = ("users",)

    list_display = ("msg", "id",)

admin.site.register(Messages, MessagesAdmin)