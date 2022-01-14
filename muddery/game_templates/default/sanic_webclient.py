# The sanic server.

from muddery.server.networks.sanic_webclient import run_webclient
from muddery.server.conf import settings
from server.settings import Settings


settings.update(Settings())

run_webclient()
