
from filebrowser import settings
from django.conf import settings as django_settings

class FileBrowserSettings(object):
    """
    Proxy for file browser settings defined at module level

    This class allows for the addition of properties to
    compute the correct setting, and makes accessing settings
    explicit in modules that use it:

    >>> from filebrowser.conf import fb_settings
    >>> fb_settings.MEDIA_ROOT # etc..
    """
    def __getattr__(self, name):
        # For MEDIA_ROOT and DIRECTORY, access Django settings dynamically
        # to support test overrides
        if name == 'MEDIA_ROOT':
            return getattr(django_settings, "FILEBROWSER_MEDIA_ROOT", django_settings.MEDIA_ROOT)
        elif name == 'DIRECTORY':
            return getattr(django_settings, "FILEBROWSER_DIRECTORY", getattr(settings, 'DIRECTORY', 'uploads/'))
        else:
            return getattr(settings, name)

fb_settings = FileBrowserSettings()
