from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class GenericManager(models.Manager):
    
    def flat_field_list_filtered(self, field, criteria={}, output="list"):
        """"
        Exports a list of a field's values as a list, dictionary or a comma seperated string
        It does not support more than one field yet.
        """
        if self.model._meta.get_field('id').get_internal_type() == "CharField":
            empty_criteria = {field:""}
        else:
            empty_criteria = {field+"__isnull":True}

        # removing empty results
        result = self.filter(**criteria).exclude(**empty_criteria).values_list(field, flat=True)
        # import pdb
        # pdb.set_trace()


        if output == "dict":
            result = dict.fromkeys(result, True)
        elif output == "str":
            result = reduce(lambda x, y: "%s,%s" % (x, y), result)
        elif output == "list_of_strings":
            result = map(str, result)

        # logger.info("flat_field_list_filtered result: %s" % result)
        
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



class Messages(models.Model):
    """
    Messages for users
    """

    objects = GenericManager()

    msg = models.CharField("Message", max_length=255)
    users = models.ManyToManyField(User, help_text="Users who need to akhnowledge this message")
    
    def __unicode__(self):
        return self.msg[:40]



