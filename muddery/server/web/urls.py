#
# File that determines what each URL points to. This uses _Python_ regular
# expressions, not Perl's.
#
# See:
# http://diveintopython.org/regular_expressions/street_addresses.html#re.matching.2.3
#
from django.conf import settings
from django.conf.urls import url, include
from django.views.static import serve
from django.views.generic import RedirectView
from muddery.worlddata.processer import PROCESSER

# Setup the root url tree from /

urlpatterns = [
    # Front page (note that we shouldn't specify namespace here since we will
    # not be able to load django-auth/admin stuff (will probably work in Django>1.9)
    url(r'^', include('muddery.web.website.urls')),#, namespace='website', app_name='website')),

    # Webclient
    url(r'^webclient/(?P<path>.*)$', serve, {'document_root': settings.WEBCLIENT_ROOT}),

    # World Editor Web
    url(r'^editor/(?P<path>.*)$', serve, {'document_root': settings.WORLDEDITOR_ROOT}),

    # World Editor API
    url(r'^' + settings.WORLD_DATA_API_PATH, PROCESSER.process),

    # favicon
    url(r'^favicon\.ico$',  RedirectView.as_view(url='/media/images/favicon.ico', permanent=False))
    ]

