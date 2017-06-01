# -*- coding: utf-8 -*-
import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.conf import settings
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .cache import FileCache

class ResubmitBaseWidget(ClearableFileInput):
    def __init__(self, attrs=None, field_type=None):
        super(ResubmitBaseWidget, self).__init__(attrs)
        self.cache_keys = []
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(ResubmitBaseWidget, self).value_from_datadict(
            data, files, name)
        if upload == FILE_INPUT_CONTRADICTION:
            return upload

        self.input_name = "%s_cache_key" % name
        self.cache_keys = data.getlist(self.input_name, [])

        if name in files:
            # Delete old files
            for cache_key in self.cache_keys:
                FileCache().delete(cache_key)
            upload = hasattr(files, 'getlist') and files.getlist(name) or files[name]
            for uploaded_file in upload:
                cache_key = self.random_key()[:10]
                FileCache().set(cache_key, uploaded_file)
                self.cache_keys.append(cache_key)
        elif self.cache_keys:
            restored = []
            for cache_key in self.cache_keys:
                restored.append(FileCache().get(cache_key, name))
            if restored:
                upload = restored
                files[name] = upload
        # Return only first element (because that's the way django file field works)
        return upload and upload[0] or None

    def random_key(self):
        return uuid.uuid4().hex

    def output_extra_data(self, value):
        output = ''
        if value and self.cache_keys:
            output += ' ' + str(_('(Uploaded files in Cache)'))
        if self.cache_keys:
            for cache_key in self.cache_keys:
                output += forms.HiddenInput().render(
                    self.input_name,
                    cache_key,
                    {},
                )
        return output

    def filename_from_value(self, value):
        if value:
            return os.path.split(value.name)[-1]


class ResubmitFileWidget(ResubmitBaseWidget):
    template_with_initial = ClearableFileInput.template_with_initial
    template_with_clear = ClearableFileInput.template_with_clear

    def render(self, name, value, attrs=None):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class ResubmitImageWidget(ResubmitFileWidget):
    pass
