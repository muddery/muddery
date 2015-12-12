"""
This is adapt from evennia/evennia/commands/default/player.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

"""
import time
from django.conf import settings
from evennia.server.sessionhandler import SESSIONS
from evennia.commands.command import Command
from evennia.utils import utils, create, search, prettytable

MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
MULTISESSION_MODE = settings.MULTISESSION_MODE

# limit symbol import for API
__all__ = ("CmdQuit")

# force max nr chars to 1 if mode is 0 or 1
MAX_NR_CHARACTERS = MULTISESSION_MODE < 2 and 1 or MAX_NR_CHARACTERS
BASE_PLAYER_TYPECLASS = settings.BASE_PLAYER_TYPECLASS

PERMISSION_HIERARCHY = settings.PERMISSION_HIERARCHY
PERMISSION_HIERARCHY_LOWER = [perm.lower() for perm in PERMISSION_HIERARCHY]

# Obs - these are all intended to be stored on the Player, and as such,
# use self.player instead of self.caller, just to be sure. Also self.msg()
# is used to make sure returns go to the right session


class CmdQuit(Command):
    """
    quit the game

    Usage:
        {"cmd":"quit",
         "args":""
        }

    Gracefully disconnect your current session from the
    game. Use the /all switch to disconnect from all sessions.
    """
    key = "quit"
    locks = "cmd:all()"

    def func(self):
        "hook function"
        player = self.player

        nsess = len(player.sessions.all())
        if nsess == 2:
            player.msg({"msg":"{RQuitting{n. One session is still connected.",
                       "logout":""},
                       session=self.session)
        elif nsess > 2:
            player.msg({"msg":"{RQuitting{n. %i session are still connected." % (nsess-1),
                       "logout":""},
                       session=self.session)
        else:
            # we are quitting the last available session
            player.msg({"msg":"{RQuitting{n. Hope to see you again, soon.",
                       "logout":""},
                       session=self.session)
        player.disconnect_session_from_player(self.session)
