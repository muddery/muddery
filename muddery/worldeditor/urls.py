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
from muddery.worldeditor.server import Server

# Setup the root url tree from /

urlpatterns = [

    # World Editor Web
    url(r'^editor/(?P<path>.*)$', serve, {'document_root': settings.WORLDEDITOR_ROOT}),

    # World Editor API
    url(r'^' + settings.WORLD_EDITOR_API_PATH, Server.inst().handle_request),

    # favicon
    url(r'^favicon\.ico$',  RedirectView.as_view(url='images/favicon.ico', permanent=False)),
]

