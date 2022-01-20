# The game server.

from muddery.server.networks.sanic_server import run_server
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


SETTINGS.update(ServerSettings())

run_server()
