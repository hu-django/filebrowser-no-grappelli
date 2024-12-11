from django.conf import settings
try:
    from django.urls import re_path as url, path
except ImportError:
    from django.conf.urls import url

from django.conf.urls import include

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from filebrowser import urls


admin.autodiscover()

urlpatterns = [
    path('admin/filebrowser/', include(urls.urlpatterns)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG or settings.ENABLE_MEDIA:
    urlpatterns += [
        url(r'^%s(?P<path>.*)$' % getattr(settings, 'MEDIA_URL', '/')[1:], serve,
            {'document_root': getattr(settings, 'MEDIA_ROOT', '/dev/null'),  'show_indexes': True}),
    ]

urlpatterns += staticfiles_urlpatterns()