"""
Some generic functions
"""

from django.core.urlresolvers import reverse
from django.core.cache import cache

import datetime

#######################
# get_or_none
#
# Example:
# 
#######################


def get_or_none(model, **kwargs):
    """
    example:
    
    foo = get_or_none(Foo, baz=bar)
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None



def int_with_default(n, default=0):
    try:
        n = int(n)
    except ValueError:
        n = default

    return n



def url_to_edit_object(object):
    return reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )


def url_to_list_view_of_object(object):
    return reverse('admin:%s_%s_changelist' % (object._meta.app_label,  object._meta.module_name))



def select_old_objects(the_model, date_field_name, older_than_days):
    """
    selects objects old than certain days ago
    If you want to for example delete these old objects, run:
    select_old_objects(the_model=ApArticle, date_field_name="date_created", older_than_days=10).delete()
    Note that model itself should be passed here and not the name of the model.
    However for date_field_name, you pass the name of the field.
    """
    older_than_days=int(older_than_days)
    date_field_name = "%s__lte" % date_field_name
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
    the_filter={
        date_field_name: time_threshold,
    }
    #it needs ** to feed the dictionary as kwargs to the filter
    return the_model.objects.filter(**the_filter)



def get_or_cache(key, time=3600,func=lambda: None):
    """
    if the key already exists in the Memcached, then it returns the value.
    Otherwise runs a function (func) and puts it in the cache
    """
 
    result = cache.get(key)
    
    if not result:
        result = func()
        cache.set(key, result, time)
    
    return result


def serial_func(key, time=3600, func=lambda: None):
    """
    sets a key in cache when running a function to make sure the same function
    can't run more than one time at once
    """
    result = None
    if cache.get(key):
        print "This function is already running"
    else:
        #setting a key that cache is running
        cache.set(key, True, 3600)
        try:
            result = func()
        finally:
            cache.delete(key)
    return result

