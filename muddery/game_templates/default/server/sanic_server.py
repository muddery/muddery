# The sanic server.

from muddery.server.connections.sanic_server import server_app
from muddery.server.conf import settings
from server.settings import Settings


settings.update(Settings())

server_app.run(port=settings.WEBSERVER_PORT)
