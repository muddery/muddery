# The sanic server.

from sanic import Sanic
from muddery.server.settings import SETTINGS


def run_webclient():
    webclient_app = Sanic("muddery_webclient")
    webclient_app.static('/webclient', SETTINGS.WEBCLIENT_ROOT)
    webclient_app.static('/media', SETTINGS.MEDIA_ROOT)

    webclient_app.run(port=SETTINGS.WEBCLIENT_PORT)
