"""
This is adapt from evennia/evennia/commands/default/unloggedin.py.
The licence of Evennia can be found in evennia/LICENSE.txt.
"""

import re
import traceback
import time
import hashlib
from collections import defaultdict
from random import getrandbits
from django.conf import settings
from evennia.players.models import PlayerDB
from evennia.objects.models import ObjectDB
from evennia.server.models import ServerConfig
from evennia.utils import logger, utils
from evennia.commands.command import Command
from evennia.commands.cmdhandler import CMD_LOGINSTART
from muddery.utils.builder import create_player, create_character
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.utils import search_obj_data_key


# limit symbol import for API
__all__ = ("CmdUnconnectedConnect", "CmdUnconnectedCreate", "CmdUnconnectedCreateConnect",
           "CmdUnconnectedQuit", "CmdUnconnectedLook")

MULTISESSION_MODE = settings.MULTISESSION_MODE

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


def create_guest_player(session):
    """
    Creates a guest player/character for this session, if one is available.

    Args:
    session (Session): the session which will use the guest player/character.

    Returns:
    GUEST_ENABLED (boolean), player (Player):
    the boolean is whether guest accounts are enabled at all.
    the Player which was created from an available guest name.
    """
    # check if guests are enabled.
    if not settings.GUEST_ENABLED:
        return False, None

    # Check IP bans.
    bans = ServerConfig.objects.conf("server_bans")
    if bans and any(tup[2].match(session.address) for tup in bans if tup[2]):
        # this is a banned IP!
        string = "{rYou have been banned and cannot continue from here." \
            "\nIf you feel this ban is in error, please email an admin.{x"
        session.msg(string)
        session.sessionhandler.disconnect(session, "Good bye! Disconnecting.")
        return True, None

    try:
        # Find an available guest name.
        playername = None
        for playername in settings.GUEST_LIST:
            if not PlayerDB.objects.filter(username__iexact=playername):
                break
            playername = None
        if playername == None:
            session.msg("All guest accounts are in use. Please try again later.")
            return True, None

        password = "%016x" % getrandbits(64)
        permissions = settings.PERMISSION_GUEST_DEFAULT
        new_player = create_player(playername, password, permissions=permissions)
        if new_player:
            create_character(new_player, playername, permissions=permissions)

    except Exception, e:
        # We are in the middle between logged in and -not, so we have
        # to handle tracebacks ourselves at this point. If we don't,
        # we won't see any errors at all.
        session.msg({"alert":_("There was an error creating the Player: %s" % e)})
        logger.log_trace()
    finally:
        return True, new_player


def create_normal_player(session, playername, password):
    """
    Create a new player.
    """
    # sanity checks
    if not re.findall('^[\w. @+-]+$', playername) or not (0 < len(playername) <= 32):
        # this echoes the restrictions made by django's auth
        # module (except not allowing spaces, for convenience of
        # logging in).
        string = "\n\r Playername can max be 32 characters or fewer. Letters, spaces, digits and @/./+/-/_ only."
        session.msg({"alert":string})
        return
    # strip excessive spaces in playername
    playername = re.sub(r"\s+", " ", playername).strip()
    if PlayerDB.objects.filter(username__iexact=playername):
        # player already exists (we also ignore capitalization here)
        session.msg({"alert":_("Sorry, there is already a player with the name '%s'.") % playername})
        return
    # Reserve playernames found in GUEST_LIST
    if settings.GUEST_LIST and playername.lower() in (guest.lower() for guest in settings.GUEST_LIST):
        string = "\n\r That name is reserved. Please choose another Playername."
        session.msg({"alert":string})
        return

    if not re.findall('^[\w. @+-]+$', password) or not (3 < len(password)):
        string = "\n\r Password should be longer than 3 characers. Letters, spaces, digits and @\.\+\-\_ only." \
                 "\nFor best security, make it longer than 8 characters. You can also use a phrase of" \
                 "\nmany words if you enclose the password in quotes."
        session.msg({"alert":string})
        return

    # Check IP and/or name bans
    bans = ServerConfig.objects.conf("server_bans")
    if bans and (any(tup[0]==playername.lower() for tup in bans)
                 or
                 any(tup[2].match(session.address) for tup in bans if tup[2])):
        # this is a banned IP or name!
        string = "{rYou have been banned and cannot continue from here." \
                 "\nIf you feel this ban is in error, please email an admin.{x"
        session.msg({"alert":string})
        session.execute_cmd('{"cmd":"quit","args":""}')
        return

    # everything's ok. Create the new player account.
    new_player = None
    try:
        new_player = create_player(playername, password)
    except Exception, e:
        # We are in the middle between logged in and -not, so we have
        # to handle tracebacks ourselves at this point. If we don't,
        # we won't see any errors at all.
        session.msg({"alert":_("There was an error creating the Player: %s" % e)})
        logger.log_tracemsg()

    return new_player


def connect_normal_player(session, name, password):
    """
    Connect a player with the given name and password.

    Args:
    session (Session): the session which is requesting to create a player.
    name (str): the name that the player wants to use for login.
    password (str): the password desired by this player, for login.

    Returns:
    player (Player): the player which was connected from the name and password.
    """
    # check for too many login errors too quick.
    if _throttle(session, maxlim=5, timeout=5*60):
        # timeout is 5 minutes.
        session.msg("{RYou made too many connection attempts. Try again in a few minutes.{n")
        return None

    # Match account name and check password
    player = PlayerDB.objects.get_player_from_name(name)
    pswd = None
    if player:
        pswd = player.check_password(password)

    if not (player and pswd):
        # No playername or password match
        session.msg({"alert":_("Incorrect username or password.")})
        # this just updates the throttle
        _throttle(session)
        # calls player hook for a failed login if possible.
        if player:
            player.at_failed_login(session)
        return None

    # Check IP and/or name bans
    bans = ServerConfig.objects.conf("server_bans")
    if bans and (any(tup[0]==player.name.lower() for tup in bans)
                 or
                 any(tup[2].match(session.address) for tup in bans if tup[2])):
        # this is a banned IP or name!
        string = "{rYou have been banned and cannot continue from here." \
            "\nIf you feel this ban is in error, please email an admin.{x"
        session.msg(string)
        session.sessionhandler.disconnect(session, "Good bye! Disconnecting.")
        return None

    return player


class CmdUnconnectedConnect(Command):
    """
    connect to the game

    Usage:
        {"cmd":"connect",
         "args":{
            "playername":<playername>,
            "password":<password>
            }
        }

    """
    key = "connect"
    locks = "cmd:all()"

    def func(self):
        """
        Uses the Django admin api. Note that unlogged-in commands
        have a unique position in that their func() receives
        a session object instead of a source_object like all
        other types of logged-in commands (this is because
        there is no object yet before the player has logged in)
        """
        session = self.caller
        args = self.args

        try:
            playername = args["playername"]
            password = args["password"]
        except Exception:
            string = 'Can not log in.'
            logger.log_errmsg(string)
            session.msg({"alert":string})
            return

        # check for too many login errors too quick.
        if _throttle(session, maxlim=5, timeout=5*60, storage=_LATEST_FAILED_LOGINS):
            # timeout is 5 minutes.
            session.msg({"alert":_("{RYou made too many connection attempts. Try again in a few minutes.{n")})
            return

        # Guest login
        if playername.lower() == "guest":
            enabled, new_player = create_guest_player(session)
            if new_player:
                session.msg({"login":{"name": playername, "dbref": new_player.dbref}})
                session.sessionhandler.login(session, new_player)
            if enabled:
                return

        if not password:
            session.msg({"alert":_("Please input password.")})
            return

        player = connect_normal_player(session, playername, password)
        if player:
            # actually do the login. This will call all other hooks:
            #   session.at_login()
            #   player.at_init()  # always called when object is loaded from disk
            #   player.at_first_login()  # only once, for player-centric setup
            #   player.at_pre_login()
            #   player.at_post_login(session=session)
            session.msg({"login":{"name": playername, "dbref": player.dbref}})
            session.sessionhandler.login(session, player)


class CmdUnconnectedCreate(Command):
    """
    create a new player account and login

    Usage:
        {"cmd":"create",
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
    locks = "cmd:all()"

    def func(self):
        "Do checks, create account and login."
        session = self.caller
        args = self.args

        try:
            playername = args["playername"]
            password = args["password"]
            connect = args["connect"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_connect",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "password":<password>,'
            string += '\n        "connect":<connect>'
            string += '\n        }'

            logger.log_errmsg(string)
            session.msg({"alert":string})
            return

        new_player = create_normal_player(session, playername, password)
        if connect:
            session.msg({"login":{"name": playername, "dbref": new_player.dbref}})
            session.sessionhandler.login(session, new_player)
        else:
            session.msg({"created":{"name": playername, "dbref": new_player.dbref}})


class CmdQuickLogin(Command):
    """
    Login only with player's name.

    Usage:
        {"cmd":"create",
         "args":{
            "playername":<playername>,
            }
        }
    """
    key = "quick_login"
    locks = "cmd:all()"

    def func(self):
        "Do checks, create account and login."
        session = self.caller
        args = self.args

        try:
            playername = args["playername"]
            md5 = hashlib.md5()
            md5.update(playername)
            name_md5 = md5.hexdigest()
        except Exception:
            string = 'Syntax error!'
            logger.log_errmsg(string)
            session.msg({"alert":string})
            return

        player = None
        character = None
        if PlayerDB.objects.filter(username__iexact=name_md5):
            # Already has this player. Login.
            player = connect_normal_player(session, name_md5, name_md5)
        else:
            # Register
            player = create_normal_player(session, name_md5, name_md5)

        if player:
            session.sessionhandler.login(session, player)
            if player.db._last_puppet:
                character = player.db._last_puppet
            elif player.db._playable_characters:
                character = player.db._playable_characters[0]
            else:
                character = create_character(player, playername)

        if character:
            try:
                player.puppet_object(session, character)
                player.db._last_puppet = character
            except RuntimeError as exc:
                session.msg({"alert":_("{rYou cannot become {C%s{n: %s") % (character.name, exc)})


class CmdUnconnectedQuit(Command):
    """
    quit when in unlogged-in state

    Usage:
        {"cmd":"quit",
         "args":""
        }

    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "quit"
    locks = "cmd:all()"

    def func(self):
        "Simply close the connection."
        session = self.caller
        #session.msg("Good bye! Disconnecting ...")
        session.sessionhandler.disconnect(session, "Good bye! Disconnecting.")


class CmdUnconnectedLook(Command):
    """
    look when in unlogged-in state

    Usage:
        {"cmd":"look",
         "args":""
        }

    This is an unconnected version of the look command for simplicity.

    This is called by the server and kicks everything in gear.
    All it does is display the connect screen.
    """
    key = "look"
    locks = "cmd:all()"

    def func(self):
        "Show the connect screen."
        connection_screen = GAME_SETTINGS.get("connection_screen")
        if not connection_screen:
            connection_screen = "No connection screen found. Please contact an admin."
        self.caller.msg({"msg":connection_screen})


class CmdUnconnectedLoginStart(Command):
    """
    login started unlogged-in state

    Usage:
        CMD_LOGINSTART

    This is an unconnected version of the look command for simplicity.

    This is called by the server and kicks everything in gear.
    All it does is display the connect screen.
    """
    key = CMD_LOGINSTART
    locks = "cmd:all()"

    def func(self):
        "Send settings to the client."
        client_settings = GAME_SETTINGS.get_client_settings()
        self.caller.msg({"settings": client_settings})

        "Show the connect screen."
        connection_screen = GAME_SETTINGS.get("connection_screen")
        if not connection_screen:
            connection_screen = "No connection screen found. Please contact an admin."
        self.caller.msg({"msg": connection_screen})
