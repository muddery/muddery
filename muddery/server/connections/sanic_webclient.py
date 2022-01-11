# The sanic server.

from sanic import Sanic
from muddery.server.conf import settings


webclient_app = Sanic("muddery_webclient")
webclient_app.static('/webclient', settings.WEBCLIENT_ROOT)
