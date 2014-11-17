# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import types
from generics.functions import datetime_difference

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class GenericManager(models.Manager):
    
    def flat_field_list_filtered(self, fields=None, field=None, criteria={}, order_by='id', output="list"):
        """"
        Exports a list of a field's values as a list, dictionary or a comma seperated string
        """
        if isinstance(field, types.StringTypes):
            fields = (field,)
            only_one_field = True
        else:
            only_one_field = False

        empty_criteria = {}

        for f in fields:
            if self.model._meta.get_field(f).get_internal_type() == "CharField":
                empty_criteria[f] = ""
            else:
                empty_criteria[f+"__isnull"] = True

        # removing empty results
        if only_one_field:
            result = self.filter(**criteria).exclude(**empty_criteria).values_list(*fields, flat=True).order_by(order_by)
            if output == "dict":
                result = dict.fromkeys(result, True)
            elif output == "str":
                result = reduce(lambda x, y: "%s,%s" % (x, y), result)
            elif output == "list_of_strings":
                result = map(str, result)
            elif output == "list":
                pass
            else:
                raise Exception("Only 'list', 'dict','str' and 'list_of_strings' as output are supported for single field input")
        else:
            if output == "list":
                result = self.filter(**criteria).exclude(**empty_criteria).order_by(order_by).values_list(*fields)
            elif output == "list_of_dict":
                result = self.filter(**criteria).exclude(**empty_criteria).order_by(order_by).values(*fields)
            elif output == "list_of_dict_due":
                result = dict(self.filter(**criteria).exclude(**empty_criteria).order_by(order_by).values_list(*fields))
            else:
                raise Exception("Only 'list' and 'list_of_dict' and 'list_of_dict_due' as output are supported for multi field input")

        
        return result


    def get_or_none(self, **kwargs):
        """
        Gives you None if no result exists instead of raising an error
        """
        try:
            return self.get(**kwargs)
        except self.DoesNotExist:
            return None


    def select_old_objects(self, date_field_name, older_than_days):
        """
        selects objects newer than certain number of days ago
        If you want to for example delete these old objects, run:
        MyModel.select_old_objects(date_field_name="date_created", older_than_days=10).delete()
        For date_field_name, you pass the name of the field.
        """
        older_than_days=int(older_than_days)
        date_field_name = "%s__lte" % date_field_name
        time_threshold = timezone.now() - timezone.timedelta(days=older_than_days)
        the_filter={
            date_field_name: time_threshold,
        }
        #it needs ** to feed the dictionary as kwargs to the filter
        return self.filter(**the_filter)






class MessagesStatus(models.Model):
    message = models.ForeignKey('Messages', related_name="status_of_user_messages")
    user = models.ForeignKey(User, related_name="status_of_messaged_users")
    akhnowledge_date = models.DateTimeField(editable=False, null=True, default=None)

    class Meta:
        unique_together = (("message", "user"),)

    def __unicode__(self):
        if self.akhnowledge_date:
            return "%s akhnowledged %s on %s" % (self.user, self.message, self.akhnowledge_date)
        else:
            return "%s has not akhnowledged %s yet" % (self.user, self.message)




class MessagesManager(GenericManager):
    
    def create_msg(self, msg, msg_code, username):
        """
        This is a simple function to message one user. If the message has been akhnowledged before
        it will pop it up again.
        """

        from django.db import IntegrityError

        try:
            message_obj = self.get(msg_code=msg_code)
        except:
            message_obj = self.create(msg=msg, msg_code=msg_code)
        else:
            message_obj.msg=msg
            message_obj.save()

        the_user = User.objects.get(username=username)
        try:
            MessagesStatus.objects.create(message=message_obj, user=the_user)
        except IntegrityError:
            ms = MessagesStatus.objects.get(message=message_obj, user=the_user)
            ms.akhnowledge_date=None
            ms.save()
        except:
            logger.error("Error when creating user message: message status:", exc_info=True)




class Messages(models.Model):
    """
    Messages for users
    """

    objects = MessagesManager()

    msg = models.CharField("Message", max_length=255, default="Message")
    msg_code = models.CharField("Message Unique Code", max_length=30, unique=True, db_index=True)
    button_txt = models.CharField("Button Text", max_length=50, default="Ok")
    button_link = models.URLField("Button Link", max_length=200, default="", blank=True)
    users = models.ManyToManyField(User, through=MessagesStatus, related_name="messages_of_user",help_text="Users who need to akhnowledge this message")


    class Meta:
        verbose_name_plural = 'Messages'
        verbose_name = 'Message'
    
    def __unicode__(self):
        return self.msg[:40]




class CeleryTasks(models.Model):
    """
    Keeps track of celery Tasks
    """
    objects = GenericManager()

    task_id = models.CharField('task id', max_length=50, unique=True, db_index=True)
    status = models.CharField('state', max_length=40, default="waiting", db_index=True)
    creation_date = models.DateTimeField('Creation Date', auto_now_add=True)
    start_date = models.DateTimeField('Start Date', null=True)
    end_date = models.DateTimeField('End Date', default=None, null=True)
    user = models.ForeignKey(User, related_name="tasks_of_user")
    key = models.CharField("Task Blocking Key", max_length=50, db_index=True, default="", blank=True)

    @property
    def duration(self):
        if self.end_date:
            try:
                duration = datetime_difference(self.start_date, self.end_date)
            except:
                duration = "Err"
        else:
            duration = "Not finished"

        return duration


    class Meta:
        verbose_name_plural = 'Tasks History'
        verbose_name = 'Task History'

    def __unicode__(self):
        return "%s: %s" % (self.task_id, self.status)


