# The sanic server.

from muddery.server.networks.sanic_server import run_server
from muddery.server.conf import settings
from server.settings import Settings


settings.update(Settings())

run_server()
