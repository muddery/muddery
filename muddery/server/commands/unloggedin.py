"""
General commands usually availabe to all users.
"""

import re
import time
from collections import defaultdict
from muddery.server.settings import SETTINGS
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.logger import logger
from muddery.server.commands.base_command import BaseCommand
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GameSettings
from muddery.server.database.worlddata.equipment_positions import EquipmentPositions
from muddery.server.database.worlddata.honour_settings import HonourSettings


# Helper function to throttle failed connection attempts.
# This can easily be used to limit player creation too,
# (just supply a different storage dictionary), but this
# would also block dummyrunner, so it's not added as default.

_LATEST_FAILED_LOGINS = defaultdict(list)
def _throttle(session, maxlim=None, timeout=None, storage=_LATEST_FAILED_LOGINS):
    """
    This will check the session's address against the
    _LATEST_LOGINS dictionary to check they haven't
    spammed too many fails recently.

    Args:
        session (Session): Session failing
        maxlim (int): max number of attempts to allow
        timeout (int): number of timeout seconds after
            max number of tries has been reached.

    Returns:
        throttles (bool): True if throttling is active,
            False otherwise.

    Notes:
        If maxlim and/or timeout are set, the function will
        just do the comparison, not append a new datapoint.

    """
    address = session.address
    if isinstance(address, tuple):
        address = address[0]
    now = time.time()
    if maxlim and timeout:
        # checking mode
        latest_fails = storage[address]
        if latest_fails and len(latest_fails) >= maxlim:
            # too many fails recently
            if now - latest_fails[-1] < timeout:
                # too soon - timeout in play
                return True
            else:
                # timeout has passed. Reset faillist
                storage[address] = []
                return False
    else:
        # store the time of the latest fail
        storage[address].append(time.time())
        return False


class CmdConnectAccount(BaseCommand):
    """
    connect to the game

    Usage:
        {
            "cmd":"connect",
            "args":{
                "playername":<playername>,
                "password":<password>
            }
        }

    """
    key = "connect"

    @classmethod
    async def func(cls, session, args):
        """
        Login the game server.
        """
        try:
            username = args["username"]
            password = args["password"]
        except Exception:
            string = 'Can not log in.'
            logger.log_err(string)
            await session.msg({"alert":string})
            return

        # check for too many login errors too quick.
        if _throttle(session, maxlim=5, timeout=5*60, storage=_LATEST_FAILED_LOGINS):
            # timeout is 5 minutes.
            await session.msg({"alert":_("{RYou made too many connection attempts. Try again in a few minutes.{n")})
            return

        if not password:
            await session.msg({"alert":_("Please input password.")})
            return

        # Get the account.
        element_type = SETTINGS.ACCOUNT_ELEMENT_TYPE
        account = ELEMENT(element_type)()

        # Set the account with username and password.
        try:
            await account.set_user(username, password)
        except MudderyError as e:
            if e.code == ERR.no_authentication:
                # Wrong username or password.
                await session.msg({"alert": str(e)})
            else:
                await session.msg({"alert": _("You can not login.")})

            # this just updates the throttle
            _throttle(session)
            return None

        # actually do the login. This will call all other hooks:
        #   session.at_login()
        #   player.at_init()  # always called when object is loaded from disk
        #   player.at_first_login()  # only once, for player-centric setup
        #   player.at_pre_login()
        #   player.at_post_login(session=session)
        await session.login(account)


class CmdCreateAccount(BaseCommand):
    """
    create a new player account and login

    Usage:
        {
            "cmd":"create",
            "args":{
                "playername":<playername>,
                "password":<password>,
                "connect":<connect>
            }
        }

    args:
        connect: (boolean)connect after created
    """
    key = "create"

    @classmethod
    async def func(cls, session, args):
        "Do checks, create account and login."
        if not args:
            await session.msg({"alert": _("Syntax error!")})
            return

        if "username" not in args:
            await session.msg({"alert": _("You should appoint a username.")})
            return

        if "password" not in args:
            await session.msg({"alert": _("You should appoint a password.")})
            return

        username = args["username"]
        username = re.sub(r"\s+", " ", username).strip()

        password = args["password"]

        connect = True
        if "connect" in args:
            connect = args["connect"]

        # Create an account.
        element_type = SETTINGS.ACCOUNT_ELEMENT_TYPE
        account = ELEMENT(element_type)()

        # Set the account with username and password.
        try:
            await account.new_user(username, password, "")
        except MudderyError as e:
            if e.code == ERR.no_authentication:
                # Wrong username or password.
                await session.msg({"alert": str(e)})
            else:
                await session.msg({"alert": _("There was an error creating the Player: %s" % e)})
            return None

        if connect:
            await session.login(account)
        else:
            await session.msg({"created":{"name": session, "id": account.get_id()}})


class CmdQuitAccount(BaseCommand):
    """
    quit when in unlogged-in state

    Usage:
        {
            "cmd":"quit",
            "args":""
        }

    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "quit"

    @classmethod
    async def func(cls, session, args):
        await session.logout()


class CmdUnloginLook(BaseCommand):
    """
    login started unlogged-in state

    Usage:
        {
            "cmd": "unloggedin_look"
        }

    This is an unconnected version of the look command for simplicity.

    This is called by the server and kicks everything in gear.
    All it does is display the connect screen.
    """
    key = "unloggedin_look"

    @classmethod
    async def func(cls, session, args):
        "Show the connect screen."
        game_name = GameSettings.inst().get("game_name")
        connection_screen = GameSettings.inst().get("connection_screen")
        honour_settings = HonourSettings.get_first_data()
        records = EquipmentPositions.all()
        equipment_pos = [{
            "key": r.key,
            "name": r.name,
            "desc": r.desc,
        } for r in records]

        await session.msg({
            "game_name": game_name,
            "conn_screen": connection_screen,
            "equipment_pos": equipment_pos,
            "min_honour_level": honour_settings.min_honour_level,
        })
