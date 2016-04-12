from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

urlpatterns = [
    url(r'^locations/', include('locations.urls', namespace="locations")),
    url(r'^logs/', include('logs.urls', namespace="logs")),
    url(r'^qcs/', include('qcs.urls', namespace="qcs")),
    #url(r'^readings/', include('readings.urls', namespace="readings")),
    url(r'^sites/', include('sites.urls', namespace="sites")),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
print(settings.STATIC_URL, settings.STATIC_ROOT)
## Route for media files in local development.
#if settings.DEBUG:
    # This serves static files and media files.
    #urlpatterns += staticfiles_urlpatterns()
    # In case media is not served correctly
    #urlpatterns += patterns('',
    #    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    #       'document_root': settings.MEDIA_ROOT,
    #        }),
    #)