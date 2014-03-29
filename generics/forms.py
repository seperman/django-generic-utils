# -*- coding: utf-8 -*-
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

from generics.models import Messages, MessagesStatus
from django.utils.datastructures import MultiValueDictKeyError

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


"""
Example data inside ModelForm:
{'files': {}, 
'is_bound': False, 
'error_class': <class 'django.forms.util.ErrorList'>, 
'empty_permitted': False, 
'fields': {'msg': <django.forms.fields.CharField object at 0x167e990>,
'users': <django.forms.fields.MultipleChoiceField object at 0x167ead0>}, 
'initial': {'msg': u'Hello!', u'id': 1L, 'users': [1L]}, 
'label_suffix': u':', 
'instance': <Messages: Hello!>,
'prefix': None, 
'_changed_data': None, 
'_validate_unique': False, 
'data': {}, 
'_errors': None, 
'auto_id': u'id_%s'}


When you change something (object already exists):

{'files': {},
'is_bound': True,
'cleaned_data': {'msg': u'Hello!', 'users': [u'1']}, 
'error_class': <class 'django.forms.util.ErrorList'>,
'empty_permitted': False,
'fields': {
    'msg': <django.forms.fields.CharField object at 0x2fe9f10>,
    'users': <django.forms.fields.MultipleChoiceField object at 0x2ddd6d0>
    }, 
'save_m2m': <function save_m2m at 0x2fff668>,
'initial': {
    'msg': u'Hello!',
    u'id': 1L, 
    'users': [1L, 2L]
    },
'label_suffix': u':', 
'instance': <Messages: Hello!>,
'prefix': None, 
'_changed_data': None,    <-- DOES NOT INCLUDE THE M2M changed data!!
'_validate_unique': True,
'data': <QueryDict:{
    u'msg': [u'Hello!'],
    u'csrfmiddlewaretoken': [u'fxBXMwgLYpgDAdYiElB2msvOmbh8rclg'],
    u'users': [u'1'],
    u'_continue': [u'Save and continue editing']
    }>,
'_errors': {},
'auto_id': u'id_%s'}

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



    def save(self, commit=True):

        # Get the unsaved model instance
        instance = forms.ModelForm.save(self, False)
        # users = self.cleaned_data['users']

        # logger.info("=================================")
        # logger.info(locals())
        # logger.info(self.__dict__)
        # logger.info("=================================")
        # for u in 
        # instance.status_of_user_messages = 
        def save_m2m():
            # import pdb;
            # pdb.set_trace();
            # sinice initial data is in a different format than target data, we convert them to compatible sets
            try:
                initial_users = set(map(unicode, self.initial['users']))
            except MultiValueDictKeyError:
                initial_users = set([])

            try:
                target_users = set(self.cleaned_data['users'])
            except MultiValueDictKeyError:
                target_users = set([])
            
            users_removed = initial_users - target_users
            users_added = target_users - initial_users

            users_added_objects = [MessagesStatus(message=self.instance, user_id=i) for i in users_added]

            # deleting removed users from M:M
            MessagesStatus.objects.filter(message=self.instance, user__in=users_removed).delete()
            MessagesStatus.objects.bulk_create(users_added_objects)
        
        self.save_m2m = save_m2m

        # # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance