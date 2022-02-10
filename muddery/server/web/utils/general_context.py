#
# This file defines global variables that will always be
# available in a view context without having to repeatedly
# include it. For this to work, this file is included in
# the settings file, in the TEMPLATE_CONTEXT_PROCESSORS
# tuple.
#

from django.conf import settings
from muddery.common.utils import utils
from muddery.server.utils.game_settings import GameSettings

# Determine the site name and server version

try:
    GAME_NAME = GameSettings.inst().get("game_name")
except AttributeError:
    GAME_NAME = "Muddery"
SERVER_VERSION = utils.get_muddery_version()


# Setup lists of the most relevant apps so
# the adminsite becomes more readable.

PLAYER_RELATED = ['Players']
GAME_ENTITIES = ['Objects', 'Scripts', 'Comms', 'Help']
GAME_SETUP = ['Permissions', 'Config']
CONNECTIONS = ['Irc', 'Imc2']
WEBSITE = ['Flatpages', 'News', 'Sites']


def general_context(request):
    """
    Returns common Evennia-related context stuff, which
    is automatically added to context of all views.
    """
    return {
        'game_name': GAME_NAME,
        'game_slogan': SERVER_VERSION,
        "language_code" : settings.LANGUAGE_CODE,
    }
