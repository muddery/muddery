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
        for playername in settings.GUEST_LIST:
            if not PlayerDB.objects.filter(username__iexact=playername):
                break
                playername = None
            if playername == None:
                session.msg("All guest accounts are in use. Please try again later.")
                return True, None

        password = "%016x" % getrandbits(64)
        home = ObjectDB.objects.get_id(settings.GUEST_HOME)
        permissions = settings.PERMISSION_GUEST_DEFAULT
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        ptypeclass = settings.BASE_GUEST_TYPECLASS
        new_player = _create_player(session, playername, password,
                                    permissions, ptypeclass)
        if new_player:
            _create_character(GAME_SETTINGS.get("default_player_character_key"), 1, session,
                              new_player, typeclass, home,
                              home, permissions, playername)

    except Exception:
        # We are in the middle between logged in and -not, so we have
        # to handle tracebacks ourselves at this point. If we don't,
        # we won't see any errors at all.
        session.msg("An error occurred. Please e-mail an admin if the problem persists.")
        logger.log_trace()
    finally:
        return True, new_player


def create_normal_player(session, name, password):
    """
    Creates a player with the given name and password.

    Args:
    session (Session): the session which is requesting to create a player.
    name (str): the name that the player wants to use for login.
    password (str): the password desired by this player, for login.

    Returns:
    player (Player): the player which was created from the name and password.
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

        try:
            playername = self.args["playername"]
            password = self.args["password"]
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
            session.msg({"alert":_("{Please input password.")})
            return

        player = create_normal_player(session, playername, password)
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
    create a new player account

    Usage:
        {"cmd":"create_account",
         "args":{
            "playername":<playername>,
            "nickname":<nickname>,
            "password":<password>
            }
        }

    """
    key = "create_account"
    locks = "cmd:all()"

    def func(self):
        "Do checks and create account"
        session = self.caller

        try:
            playername = self.args["playername"]
            nickname = self.args["nickname"]
            password = self.args["password"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_account",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "nickname":<nickname>,'
            string += '\n        "password":<password>'
            string += '\n        }'

            logger.log_errmsg(string)
            self.caller.msg({"alert":string})
            return


        # sanity checks
        if not re.findall('^[\w. @+-]+$', playername) or not (0 < len(playername) <= 30):
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
            session.msg({"alert":_("Sorry, there is already a player with the name '%s'.") % playername})
            return
        # Reserve playernames found in GUEST_LIST
        if settings.GUEST_LIST and playername.lower() in (guest.lower() for guest in settings.GUEST_LIST):
            string = "\n\r That name is reserved. Please choose another Playername."
            session.msg({"alert":string})
            return

        # sanity checks
        if not (0 < len(nickname) <= 30):
            # Nickname's length
            string = "\n\r Nickname can max be 30 characters or fewer."
            session.msg({"alert":string})
            return
        # strip excessive spaces in playername
        nickname = re.sub(r"\s+", " ", nickname).strip()

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
        try:
            permissions = settings.PERMISSION_PLAYER_DEFAULT
            typeclass = settings.BASE_CHARACTER_TYPECLASS
            new_player = _create_player(session, playername, password, permissions)
            if new_player:
                if MULTISESSION_MODE < 2:
                    default_home = settings.DEFAULT_HOME
                    try:
                        default_home_key = GAME_SETTINGS.get("default_player_home_key")
                        if default_home_key:
                            rooms = search_obj_data_key(default_home_key)
                            default_home = rooms[0]
                    except:
                        pass

                    start_location = default_home
                    try:
                        start_location_key = GAME_SETTINGS.get("start_location_key")
                        if start_location_key:
                            rooms = search_obj_data_key(start_location_key)
                            start_location = rooms[0]
                    except:
                        pass

                    _create_character(GAME_SETTINGS.get("default_player_character_key"), 1, session,
                                      new_player, typeclass, start_location,
                                      default_home, permissions, nickname)
                # tell the caller everything went well.
                session.msg({"created":playername})

        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
            session.msg({"alert":string % (traceback.format_exc())})
            logger.log_tracemsg()


class CmdUnconnectedCreateConnect(Command):
    """
    create a new player account and login

    Usage:
        {"cmd":"create_connect",
         "args":{
            "playername":<playername>,
            "nickname":<nickname>,
            "password":<password>
            }
        }

    """
    key = "create_connect"
    locks = "cmd:all()"

    def func(self):
        "Do checks, create account and login."
        session = self.caller

        try:
            playername = self.args["playername"]
            nickname = self.args["nickname"]
            password = self.args["password"]
        except Exception:
            string = 'Syntax error!'
            string += '\nUsage:'
            string += '\n    {"cmd":"create_connect",'
            string += '\n    "args":{'
            string += '\n        "playername":<playername>,'
            string += '\n        "nickname":<nickname>,'
            string += '\n        "password":<password>'
            string += '\n        }'

            logger.log_errmsg(string)
            self.caller.msg({"alert":string})
            return

        # sanity checks
        if not re.findall('^[\w. @+-]+$', playername) or not (0 < len(playername) <= 30):
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
            session.msg({"alert":_("Sorry, there is already a player with the name '%s'.") % playername})
            return
        # Reserve playernames found in GUEST_LIST
        if settings.GUEST_LIST and playername.lower() in (guest.lower() for guest in settings.GUEST_LIST):
            string = "\n\r That name is reserved. Please choose another Playername."
            session.msg({"alert":string})
            return

        # sanity checks
        if not (0 < len(nickname) <= 30):
            # Nickname's length
            string = "\n\r Nickname can max be 30 characters or fewer."
            session.msg({"alert":string})
            return
        # strip excessive spaces in playername
        nickname = re.sub(r"\s+", " ", nickname).strip()

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
        try:
            permissions = settings.PERMISSION_PLAYER_DEFAULT
            typeclass = settings.BASE_CHARACTER_TYPECLASS
            new_player = _create_player(session, playername, password, permissions)
            if new_player:
                if MULTISESSION_MODE < 2:
                    default_home = settings.DEFAULT_HOME
                    try:
                        default_home_key = GAME_SETTINGS.get("default_player_home_key")
                        if default_home_key:
                            rooms = search_obj_data_key(default_home_key)
                            default_home = rooms[0]
                    except:
                        pass

                    start_location = default_home
                    try:
                        start_location_key = GAME_SETTINGS.get("start_location_key")
                        if start_location_key:
                            rooms = search_obj_data_key(start_location_key)
                            start_location = rooms[0]
                    except:
                        pass

                    _create_character(GAME_SETTINGS.get("default_player_character_key"), 1, session,
                                      new_player, typeclass, start_location,
                                      default_home, permissions, nickname)
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
            logger.log_tracemsg()


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


def _create_player(session, playername, password, permissions, typeclass=None):
    """
    Helper function, creates a player of the specified typeclass.
    """
    try:
        new_player = create.create_player(playername, None, password,
                                          permissions=permissions, typeclass=typeclass)

    except Exception as e:
        session.msg("There was an error creating the Player:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False

    # This needs to be set so the engine knows this player is
    # logging in for the first time. (so it knows to call the right
    # hooks during login later)
    new_player.db.FIRST_LOGIN = True

    # join the new player to the public channel
    pchannel = ChannelDB.objects.get_channel(settings.DEFAULT_CHANNELS[0]["key"])
    if not pchannel.connect(new_player):
        string = "New player '%s' could not connect to public channel!" % new_player.key
        logger.log_err(string)
    return new_player


def _create_character(character_key, level, session,
                      new_player, typeclass, location,
                      home, permissions, nickname):
    """
    Helper function, creates a character based on a player's name.
    This is meant for Guest and MULTISESSION_MODE < 2 situations.
    """
    try:
        new_character = create.create_object(typeclass, key=new_player.key, location=location,
                                             home=home, permissions=permissions)

        # set character info
        new_character.set_data_key(character_key)
        new_character.set_level(level)

        # set playable character list
        new_player.db._playable_characters.append(new_character)

        # allow only the character itself and the player to puppet this character (and Immortals).
        new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                (new_character.id, new_player.id))

        # If no description is set, set a default description
        if not new_character.db.desc:
            new_character.db.desc = "This is a Player."

        # Add nickname
        if not nickname:
            nickname = character_key
        new_character.set_nickname(nickname)
        
        # We need to set this to have @ic auto-connect to this character
        new_player.db._last_puppet = new_character
    except Exception as e:
        session.msg("There was an error creating the Character:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False

