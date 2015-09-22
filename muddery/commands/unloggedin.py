"""
This is adapt from evennia/evennia/commands/default/unloggedin.py.
The licence of Evennia can be found in evennia/LICENSE.txt.
"""

import re
import traceback
import time
from collections import defaultdict
from random import getrandbits
from django.conf import settings
from evennia.players.models import PlayerDB
from evennia.objects.models import ObjectDB
from evennia.server.models import ServerConfig
from evennia.comms.models import ChannelDB

from evennia.utils import create, logger, utils
from evennia.commands.command import Command
from evennia.commands.cmdhandler import CMD_LOGINSTART

# limit symbol import for API
__all__ = ("CmdUnconnectedConnect", "CmdUnconnectedCreate", "CmdUnconnectedCreateConnect",
           "CmdUnconnectedQuit", "CmdUnconnectedLook")

MULTISESSION_MODE = settings.MULTISESSION_MODE
CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE

# Helper function to throttle failed connection attempts.
# This can easily be used to limit player creation too,
# (just supply a different storage dictionary), but this
# would also block dummyrunner, so it's not added as default.

_LATEST_FAILED_LOGINS = defaultdict(list)
def _throttle(session, maxlim=None, timeout=None,
              storage=_LATEST_FAILED_LOGINS):
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

    This creates a new player account.
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

        try:
            playername = self.args["playername"]
            password = self.args["password"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_account",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "password":<password>'
            string += '\n        }'

            logger.log_errmsg(string)
            self.caller.msg({"alert":string})
            return

        # check for too many login errors too quick.
        if _throttle(session, maxlim=5, timeout=5*60, storage=_LATEST_FAILED_LOGINS):
            # timeout is 5 minutes.
            session.msg({"alert":"{RYou made too many connection attempts. Try again in a few minutes.{n"})
            return

        # Guest login
        if playername.lower() == "guest" and settings.GUEST_ENABLED:
            try:
                # Find an available guest name.
                for playername in settings.GUEST_LIST:
                    if not PlayerDB.objects.filter(username__iexact=playername):
                        break
                    playername = None
                if playername == None:
                    session.msg({"alert":"All guest accounts are in use. Please try again later."})
                    return

                password = "%016x" % getrandbits(64)
                home = ObjectDB.objects.get_id(settings.GUEST_HOME)
                permissions = settings.PERMISSION_GUEST_DEFAULT
                typeclass = settings.BASE_CHARACTER_TYPECLASS
                ptypeclass = settings.BASE_GUEST_TYPECLASS
                new_player = _create_player(session, playername, password,
                                            permissions, ptypeclass)
                if new_player:
                    _create_character(settings.DEFAULT_PLAYER_CHARACTER_KEY, 1,
                                      session, new_player, typeclass,
                                      home, permissions)
                    session.sessionhandler.login(session, new_player)

            except Exception:
                # We are in the middle between logged in and -not, so we have
                # to handle tracebacks ourselves at this point. If we don't,
                # we won't see any errors at all.
                string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
                session.msg({"alert":string % (traceback.format_exc())})
                logger.log_errmsg(traceback.format_exc())

            return

        # Match account name and check password
        player = PlayerDB.objects.get_player_from_name(playername)
        pswd = None
        if player:
            pswd = player.check_password(password)

        if not (player and pswd):
            # No playername or password match
            string = "Wrong login information given.\nIf you have spaces in your name or " \
                     "password, don't forget to enclose it in quotes. Also capitalization matters." \
                     "\nIf you are new you should first create a new account " \
                     "using the 'create' command."
            session.msg({"alert":string})
            # this just updates the throttle
            _throttle(session, storage=_LATEST_FAILED_LOGINS)
            return

        # Check IP and/or name bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (any(tup[0] == player.name.lower() for tup in bans)
                     or
                     any(tup[2].match(session.address) for tup in bans if tup[2])):
            # this is a banned IP or name!
            string = "{rYou have been banned and cannot continue from here." \
                     "\nIf you feel this ban is in error, please email an admin.{x"
            session.msg({"alert":string})
            session.execute_cmd('{"cmd":"quit","args":""}')
            return

        # actually do the login. This will call all other hooks:
        #   session.at_login()
        #   player.at_init()  # always called when object is loaded from disk
        #   player.at_pre_login()
        #   player.at_first_login()  # only once
        #   player.at_post_login(sessid=sessid)
        session.msg({"login":{"name": playername, "dbref": player.dbref}})
        session.sessionhandler.login(session, player)


class CmdUnconnectedCreate(Command):
    """
    create a new player account

    Usage:
        {"cmd":"create_account",
         "args":{
            "playername":<playername>,
            "password":<password>
            }
        }

    This creates a new player account.
    """
    key = "create_account"
    locks = "cmd:all()"

    def func(self):
        "Do checks and create account"
        session = self.caller

        try:
            playername = self.args["playername"]
            password = self.args["password"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_account",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "password":<password>'
            string += '\n        }'

            logger.log_errmsg(string)
            self.caller.msg({"alert":string})
            return

        # sanity checks
        if not re.findall(r'^[\w. @+-]+$', playername) or not (0 < len(playername) <= 30):
            # this echoes the restrictions made by django's auth
            # module (except not allowing spaces, for convenience of
            # logging in).
            string = "\n\r Playername can max be 30 characters or fewer. Letters, spaces, digits and @/./+/-/_ only."
            session.msg({"alert":string})
            return
        # strip excessive spaces in playername
        playername = re.sub(r"\s+", " ", playername).strip()
        if PlayerDB.objects.filter(username__iexact=playername):
            # player already exists (we also ignore capitalization here)
            session.msg({"alert":"Sorry, there is already a player with the name '%s'." % playername})
            return
        # Reserve playernames found in GUEST_LIST
        if settings.GUEST_LIST and playername.lower() in map(str.lower, settings.GUEST_LIST):
            string = "\n\r That name is reserved. Please choose another Playername."
            session.msg({"alert":string})
            return
        if not re.findall(r'^[\w. @+-]+$', password) or not (3 < len(password)):
            string = "\n\r Password should be longer than 3 characers. Letters, spaces, " \
                     "digits and @\\.\\+\\-\\_ only." \
                     "\nFor best security, make it longer than 8 characters. You can also use a phrase of" \
                     "\nmany words if you enclose the password in quotes."
            session.msg({"alert":string})
            return

        # Check IP and/or name bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (any(tup[0] == playername.lower() for tup in bans)
                     or
                     any(tup[2].match(session.address) for tup in bans if tup[2])):
            # this is a banned IP or name!
            string = "{rYou have been banned and cannot continue from here." \
                     "\nIf you feel this ban is in error, please email an admin.{x"
            session.msg({"alert":string})
            session.execute_cmd('{"cmd":"quit","args":""}')
            return

        # everything's ok. Create the new player account.
        try:
            permissions = settings.PERMISSION_PLAYER_DEFAULT
            typeclass = settings.BASE_CHARACTER_TYPECLASS
            new_player = _create_player(session, playername, password, permissions)
            if new_player:
                if MULTISESSION_MODE < 2:
                    default_home = ObjectDB.objects.get_id(settings.DEFAULT_PLAYER_HOME)
                    _create_character(settings.DEFAULT_PLAYER_CHARACTER_KEY, 1,
                                      session, new_player, typeclass,
                                      default_home, permissions)
                # tell the caller everything went well.
                session.msg({"created":playername})

        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
            session.msg({"alert":string % (traceback.format_exc())})
            logger.log_errmsg(traceback.format_exc())


class CmdUnconnectedCreateConnect(Command):
    """
    create a new player account and login

    Usage:
        {"cmd":"create_connect",
         "args":{
            "playername":<playername>,
            "password":<password>
            }
        }

    This creates a new player account.
    """
    key = "create_connect"
    locks = "cmd:all()"

    def func(self):
        "Do checks, create account and login."
        session = self.caller

        try:
            playername = self.args["playername"]
            password = self.args["password"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_connect",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "password":<password>'
            string += '\n        }'

            logger.log_errmsg(string)
            self.caller.msg({"alert":string})
            return

        # sanity checks
        if not re.findall(r'^[\w. @+-]+$', playername) or not (0 < len(playername) <= 30):
            # this echoes the restrictions made by django's auth
            # module (except not allowing spaces, for convenience of
            # logging in).
            string = "\n\r Playername can max be 30 characters or fewer. Letters, spaces, digits and @/./+/-/_ only."
            session.msg({"alert":string})
            return
        # strip excessive spaces in playername
        playername = re.sub(r"\s+", " ", playername).strip()
        if PlayerDB.objects.filter(username__iexact=playername):
            # player already exists (we also ignore capitalization here)
            session.msg({"alert":"Sorry, there is already a player with the name '%s'." % playername})
            return
        # Reserve playernames found in GUEST_LIST
        if settings.GUEST_LIST and playername.lower() in map(str.lower, settings.GUEST_LIST):
            string = "\n\r That name is reserved. Please choose another Playername."
            session.msg({"alert":string})
            return
        if not re.findall(r'^[\w. @+-]+$', password) or not (3 < len(password)):
            string = "\n\r Password should be longer than 3 characers. Letters, spaces, " \
                     "digits and @\\.\\+\\-\\_ only." \
                     "\nFor best security, make it longer than 8 characters. You can also use a phrase of" \
                     "\nmany words if you enclose the password in quotes."
            session.msg({"alert":string})
            return

        # Check IP and/or name bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (any(tup[0] == playername.lower() for tup in bans)
                     or
                     any(tup[2].match(session.address) for tup in bans if tup[2])):
            # this is a banned IP or name!
            string = "{rYou have been banned and cannot continue from here." \
                     "\nIf you feel this ban is in error, please email an admin.{x"
            session.msg({"alert":string})
            session.execute_cmd('{"cmd":"quit","args":""}')
            return

        # everything's ok. Create the new player account.
        try:
            permissions = settings.PERMISSION_PLAYER_DEFAULT
            typeclass = settings.BASE_CHARACTER_TYPECLASS
            new_player = _create_player(session, playername, password, permissions)
            if new_player:
                if MULTISESSION_MODE < 2:
                    default_home = ObjectDB.objects.get_id(settings.DEFAULT_PLAYER_HOME)
                    _create_character(settings.DEFAULT_PLAYER_CHARACTER_KEY, 1,
                                      session, new_player, typeclass,
                                      default_home, permissions)
                # tell the caller everything went well.
                # string = "A new account '%s' was created. Welcome!"
                # if " " in playername:
                #     string += "\n\nYou can now log in with the command 'connect \"%s\" <your password>'."
                # else:
                #     string += "\n\nYou can now log with the command 'connect %s <your password>'."
                # session.msg(string % (playername, playername))

                # actually do the login. This will call all other hooks:
                #   session.at_login()
                #   player.at_init()  # always called when object is loaded from disk
                #   player.at_pre_login()
                #   player.at_first_login()  # only once
                #   player.at_post_login(sessid=sessid)
                session.msg({"login":{"name": playername, "dbref": new_player.dbref}})
                session.sessionhandler.login(session, new_player)

        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
            session.msg({"alert":string % (traceback.format_exc())})
            logger.log_errmsg(traceback.format_exc())


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
        connection_screen = utils.random_string_from_module(CONNECTION_SCREEN_MODULE)
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
        "Show the connect screen."
        connection_screen = utils.random_string_from_module(CONNECTION_SCREEN_MODULE)
        if not connection_screen:
            connection_screen = "No connection screen found. Please contact an admin."
        self.caller.msg({"msg":connection_screen})


def _create_player(session, playername, password, permissions, typeclass=None):
    """
    Helper function, creates a player of the specified typeclass.
    """
    try:
        new_player = create.create_player(playername, None, password,
                                          permissions=permissions, typeclass=typeclass)

    except Exception, e:
        session.msg("There was an error creating the Player:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False

    # This needs to be called so the engine knows this player is
    # logging in for the first time. (so it knows to call the right
    # hooks during login later)
    utils.init_new_player(new_player)

    # join the new player to the public channel
    pchannel = ChannelDB.objects.get_channel(settings.DEFAULT_CHANNELS[0]["key"])
    if not pchannel.connect(new_player):
        string = "New player '%s' could not connect to public channel!" % new_player.key
        logger.log_errmsg(string)
    return new_player


def _create_character(character_key, level, session, new_player, typeclass, home, permissions):
    """
    Helper function, creates a character based on a player's name.
    This is meant for Guest and MULTISESSION_MODE < 2 situations.
    """
    try:
        new_character = create.create_object(typeclass, key=new_player.key,
                                             home=home, permissions=permissions)

        # set character info
        new_character.set_data_info(character_key)
        new_character.set_level(level)

        # set playable character list
        new_player.db._playable_characters.append(new_character)

        # allow only the character itself and the player to puppet this character (and Immortals).
        new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                (new_character.id, new_player.id))

        # If no description is set, set a default description
        if not new_character.db.desc:
            new_character.db.desc = "This is a Player."
        # We need to set this to have @ic auto-connect to this character
        new_player.db._last_puppet = new_character
    except Exception, e:
        session.msg("There was an error creating the Character:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False

