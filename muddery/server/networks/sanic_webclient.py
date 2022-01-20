# The sanic server.

from sanic import Sanic
from muddery.server.settings import settings


def run_webclient():
    webclient_app = Sanic("muddery_webclient")
    webclient_app.static('/webclient', settings.WEBCLIENT_ROOT)
    webclient_app.static('/media', settings.MEDIA_ROOT)

    webclient_app.run(port=settings.WEBCLIENT_PORT)
