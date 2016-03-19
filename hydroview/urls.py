from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import include, patterns, url

urlpatterns = [
    url(r'^locations/', include('locations.urls', namespace="locations")),
    url(r'^loggers/', include('loggers.urls', namespace="loggers")),
    url(r'^logs/', include('logs.urls', namespace="logs")),
    url(r'^qcs/', include('qcs.urls', namespace="qcs")),
    #url(r'^readings/', include('readings.urls', namespace="readings")),
    url(r'^sites/', include('sites.urls', namespace="sites")),
    url(r'^admin/', include(admin.site.urls)),
]

# Route for media files in local development.
if settings.DEBUG:
    # This serves static files and media files.
    urlpatterns += staticfiles_urlpatterns()
    # In case media is not served correctly
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    )