
from django.conf import settings
try:
    import pylibmc
except ImportError:
    def pylibmc():
        pass

# This has more functionalities than Django Cache module
# http://sendapatch.se/projects/pylibmc/reference.html
class Client(pylibmc.Client):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)


    def set(self, key, val, time=0):
        return super(Client, self).set(key.encode('ascii','ignore'), val, time)


    def replace(self, key, val, time=0):
        return super(Client, self).replace(key.encode('ascii','ignore'), val, time)


    def get(self, key):
        return super(Client, self).get(key.encode('ascii','ignore'))


    def append(self, key, val):
        return super(Client, self).append(key.encode('ascii','ignore'), val)


    def delete(self, key):
        return super(Client, self).delete(key.encode('ascii','ignore'))
 


cache = Client(settings.GENERICS_CACHE_LOCATIONS)
