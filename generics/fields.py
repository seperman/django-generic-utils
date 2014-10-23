# -*- coding: utf-8 -*-
"""
partly based on Federico Capoano script
"""



from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
import imghdr


class RestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg', 'text/csv',]
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.file_extensions = [i.split("/")[1] for i in self.content_types]
        self.max_upload_size = kwargs.pop("max_upload_size")
        self.image_content_types = ('image/jpeg', 'image/png',)

        super(RestrictedFileField, self).__init__(*args, **kwargs)


    def clean(self, *args, **kwargs):

        data = super(RestrictedFileField, self).clean(*args, **kwargs)
        
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
                if content_type in self.image_content_types and imghdr.what(file) not in self.file_extensions:
                    raise forms.ValidationError(_('Filetype not supported.'))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass
            
        return data


    def deconstruct(self):
        name, path, args, kwargs = super(RestrictedFileField, self).deconstruct()
        if self.content_types:
            kwargs['content_types'] = self.content_types
        if self.max_upload_size:
            kwargs['max_upload_size'] = self.max_upload_size
        return name, path, args, kwargs

