# The sanic server.

import os
from muddery.common.networks.sanic_server import SanicServer
from muddery.launcher.manager import collect_webclient_static
from muddery.server.settings import SETTINGS


class SanicWebclient(SanicServer):
    server_name = SETTINGS.WEBCLIENT_SERVER_NAME
    host = SETTINGS.ALLOWED_HOST
    port = SETTINGS.WEBCLIENT_PORT

    @classmethod
    def add_statics(cls, app):
        super(SanicWebclient, cls).add_statics(app)

        app.static("/", os.path.join(SETTINGS.WEBCLIENT_ROOT, "index.html"), name="index")
        app.static("/", SETTINGS.WEBCLIENT_ROOT, name="root")
        app.static("/media", SETTINGS.MEDIA_ROOT, name="media")

    @classmethod
    async def _run_before_server_start(cls, app, loop):
        await super(SanicWebclient, cls)._run_before_server_start(app, loop)

        collect_webclient_static()
