from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

from generics.models import Messages


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MessagesForm(forms.ModelForm):
    class Meta:
        model = Messages


    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)


    # Overriding __init__ here allows us to provide initial
    # data for 'users' field
    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        
        if 'instance' in kwargs:
            
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.                
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data.
            initial['users'] = [t.pk for t in User.objects.all()]            
            
        forms.ModelForm.__init__(self, *args, **kwargs)
