# The sanic server.

from muddery.server.connections.sanic_webclient import webclient_app
from muddery.server.conf import settings
from server.settings import Settings


settings.update(Settings())

webclient_app.run(port=settings.WEBCLIENT_PORT)
