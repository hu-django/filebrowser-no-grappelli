import filebrowser.fields

__author__ = 'andriy'

from django.db import models


class Object(models.Model):
    file = filebrowser.fields.FileBrowseField(name="file", max_length=200)
