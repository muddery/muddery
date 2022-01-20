# The game's webclient.

from muddery.server.networks.sanic_webclient import run_webclient
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


SETTINGS.update(ServerSettings())

run_webclient()
