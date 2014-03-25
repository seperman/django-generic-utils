from __future__ import print_function

"""
Some generic functions
"""

from django.core.urlresolvers import reverse
from django.core.cache import cache
import httplib
from urlparse import urlparse

# import datetime


def int_with_default(n, default=0):
    """
    convert to int. if not possible then use a default value
    example:
    "3" -> 3
    "sas" -> 0
    """

    try:
        n = int(n)
    except ValueError:
        n = default

    return n



def url_to_edit_object(obj):
    """
    url to edit an object in admin
    """
    return reverse('admin:%s_%s_change' %(obj._meta.app_label,  obj._meta.module_name),  args=[obj.id] )


def url_to_list_view_of_object(obj):
    """
    url to list view of an object in admin
    """
    return reverse('admin:%s_%s_changelist' % (obj._meta.app_label,  obj._meta.module_name))





def get_or_cache(key, time=3600,func=lambda: None, kwargs={}):
    """
    if the key already exists in the Memcached, then it returns the value.
    Otherwise runs a function (func) and puts it in the cache
    """
 
    result = cache.get(key)
    
    if not result:
        result = func(**kwargs)
        cache.set(key, result, time)
    
    return result


def serial_func(key, time=3600, func=lambda: None, kwargs={}):
    """
    sets a key in cache when running a function to make sure the same function
    can't run more than one time at once.
    It will clear the key if the function raises any errors.
    """
    result = None
    if cache.get(key):
        print ("This function is already running")
    else:
        #setting a key that cache is running
        cache.set(key, True, time)
        try:
            result = func(**kwargs)
        finally:
            cache.delete(key)
    return result



def serial_block_check(key):
    return cache.get(key)



def serial_block_begin(key, time=120):
    """
    sets a key in cache when running a block of code to make sure the same block
    can't run more than one time at once. This is useful for example in Celery tasks.
    """
    if cache.get(key):
        print ("This function is already running")
        return True
    else:
        #setting a key that cache is running
        cache.set(key, True, time)
        return False


def serial_block_end(key):
    """
    works in conjunction of the serial_block_begin to let the function run again.
    """
    cache.delete(key)



def model_fields_list(m):
    """
    returns a list of a Django model's fields
    """
    return m._meta.get_all_field_names() 


def model_field_type(m, f):
    """
    returns a mode's field's type (ie. Integer field or ...)
    """
    return m._meta.get_field(f).get_internal_type()


def url_exists(url, timeout=10):
    """
    Checks if a URL exists. Returns True if it can check.
    Otherwise it will return False if the URL didn't return 200 code.
    It will raise an error if the protocol is not supported.

    HTTP codes: 
    http://docs.python.org/2/library/httplib.html
    
    Example:
    url="http://hello.com/img/2014/02/08/Cushion_-_loose_stone_1.jpg"
    url_exists(url)
    True
    """
    o = urlparse(url)
    #
    if o.scheme=="http":
        conn = httplib.HTTPConnection(o.netloc, 80, timeout=timeout)
        conn.request('HEAD', o.path)
        response = conn.getresponse()
        conn.close()
        if response.status == 200:
            result = True
        else:
            result = response.status
    else:
        raise Exception("%s protocol is not implemented yet in Django Generic Utils" % o.scheme)
    return result


