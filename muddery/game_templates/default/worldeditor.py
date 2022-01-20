# The world editor.

from muddery.worldeditor.networks.sanic_server import run_server
from muddery.worldeditor.settings import SETTINGS
from worldeditor.settings import ServerSettings


SETTINGS.update(ServerSettings())

run_server()