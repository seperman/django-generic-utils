from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

from generics.models import Messages, MessagesStatus


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


"""
Example data inside ModelForm:
{'files': {}, 'is_bound': False, 'error_class': <class 'django.forms.util.ErrorList'>, 'empty_permitted': False, 'fields
': {'msg': <django.forms.fields.CharField object at 0x167e990>, 'users': <django.forms.fields.MultipleChoiceField object
 at 0x167ead0>}, 'initial': {'msg': u'Hello!', u'id': 1L, 'users': [1L]}, 'label_suffix': u':', 'instance': <Messages: H
ello!>, 'prefix': None, '_changed_data': None, '_validate_unique': False, 'data': {}, '_errors': None, 'auto_id': u'id_%
s'}
"""


class MessagesForm(forms.ModelForm):
    class Meta:
        model = Messages



    users = forms.MultipleChoiceField()


    def __init__(self,*args,**kwargs):
        super(MessagesForm, self).__init__(*args,**kwargs)



# if 1:
#     if 1:
        users_objects = User.objects.all().only("pk", "username",)
        choices = []        
        for u in users_objects:
            try:
                akhnowledge_text = u.status_of_messaged_users.get(message__pk=self.instance.pk).akhnowledge_date  #
                if akhnowledge_text:
                    akhnowledge_text = "- on %s" % akhnowledge_text.strftime('%Y-%m-%d')
                else:
                    akhnowledge_text = "- not yet"
            except MessagesStatus.DoesNotExist:
                akhnowledge_text = ""
            #
            name = "%s %s" % (u.username, akhnowledge_text)
            #
            choices.append((u.pk, name))


        self.fields['users'] = forms.MultipleChoiceField(
            widget=FilteredSelectMultiple(
                verbose_name = "Users",
                is_stacked = False,
                ),
            choices = choices,
            required=False,
            )



    # # Overriding __init__ here allows us to provide initial
    # # data for 'users' field
    # def __init__(self, *args, **kwargs):
    #     # Only in case we build the form from an instance
        
    #     if 'instance' in kwargs:
            
    #         # We get the 'initial' keyword argument or initialize it
    #         # as a dict if it didn't exist.                
    #         initial = kwargs.setdefault('initial', {})
    #         # The widget for a ModelMultipleChoiceField expects
    #         # a list of primary key for the selected data.
    #         initial['users'] = [t.pk for t in User.objects.all()]            
            
    #     forms.ModelForm.__init__(self, *args, **kwargs)
