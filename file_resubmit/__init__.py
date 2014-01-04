# coding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.core.exceptions import ImproperlyConfigured


if not 'file_resubmit' in settings.CACHES:
    raise ImproperlyConfigured("CACHES['file_resubmit'] is not defined in settings.py")
