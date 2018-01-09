"""
This is adapt from evennia/evennia/commands/default/player.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

"""

from __future__ import print_function

import time
import re
from django.conf import settings
from evennia.server.sessionhandler import SESSIONS
from evennia.commands.command import Command
from evennia.utils import create, search, logger
from evennia.utils.utils import make_iter
from muddery.utils import utils
from muddery.utils.localized_strings_handler import _
from muddery.utils.builder import create_player, create_character
from muddery.dao.honours_mapper import HONOURS_MAPPER

MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
MULTISESSION_MODE = settings.MULTISESSION_MODE

# limit symbol import for API
__all__ = ("CmdQuit")

# force max nr chars to 1 if mode is 0 or 1
MAX_NR_CHARACTERS = MULTISESSION_MODE < 2 and 1 or MAX_NR_CHARACTERS
BASE_ACCOUNT_TYPECLASS = settings.BASE_ACCOUNT_TYPECLASS

PERMISSION_HIERARCHY = settings.PERMISSION_HIERARCHY
PERMISSION_HIERARCHY_LOWER = [perm.lower() for perm in PERMISSION_HIERARCHY]

# Obs - these are all intended to be stored on the Player, and as such,
# use self.player instead of self.caller, just to be sure. Also self.msg()
# is used to make sure returns go to the right session


class CmdQuit(Command):
    """
    Quit the game.

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
        session = self.session
        player = self.account

        nsess = len(player.sessions.all())
        if nsess == 2:
            session.msg({"msg":"{RQuitting{n. One session is still connected.",
                       "logout":""},
                       session=session)
        elif nsess > 2:
            session.msg({"msg":"{RQuitting{n. %i session are still connected." % (nsess-1),
                       "logout":""},
                       session=session)
        else:
            # we are quitting the last available session
            session.msg({"msg":"{RQuitting{n. Hope to see you again, soon.",
                       "logout":""},
                       session=session)
        player.disconnect_session_from_account(session)


class CmdPuppet(Command):
    """
    Control an object you have permission to puppet

    Usage:
        {"cmd":"puppet",
         "args":<object's dbref>
        }

    Puppet a given Character.

    This will attempt to "become" a different character assuming you have
    the right to do so. Note that it's the PLAYER character that puppets
    characters/objects and which needs to have the correct permission!

    """
    key = "puppet"
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    def func(self):
        """
        Main puppet method
        """
        session = self.session
        player = self.account
        args = self.args

        # Find the character to puppet.
        new_character = None
        if args:
            # search for a matching character
            new_character = [char for char in search.object_search(args) if char.access(player, "puppet")]
            if not new_character:
                session.msg({"alert":_("That is not a valid character choice.")})
                return
            new_character = new_character[0]
        else: 
            # Puppet last character.
            new_character = player.db._last_puppet
            if not new_character:
                session.msg({"alert":_("You should puppet a character.")})
                return

        try:
            player.puppet_object(session, new_character)
            player.db._last_puppet = new_character
        except RuntimeError as exc:
            session.msg({"alert":_("{rYou cannot become {C%s{n: %s") % (new_character.name, exc)})


class CmdUnpuppet(Command):
    """
    stop puppeting

    Usage:
        {"cmd":"unpuppet",
         "args":""
        }

    Go out-of-character (OOC).

    This will leave your current character and put you in a incorporeal OOC state.
    """

    key = "unpuppet"
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    def func(self):
        "Implement function"

        player = self.account
        session = self.session

        old_char = player.get_puppet(session)
        if not old_char:
            return

        player.db._last_puppet = old_char

        # disconnect
        try:
            player.unpuppet_object(session)
            session.msg({"unpuppet": True})
        except RuntimeError as exc:
            session.msg({"alert":_("{rCould not unpuppet from {c%s{n: %s" % (old_char, exc))})
            

class CmdCharCreate(Command):
    """
    Create a new character

    Usage:
        {"cmd":"char_create",
         "args":{"name": <character's name>}
        }

    Create a new character with a name.
    """
    key = "char_create"
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    def func(self):
        "create the new character"
        session = self.session
        player = self.account
        args = self.args
        
        if not args:
            session.msg({"alert":_("You should give the character a name.")})
            return
        
        name = args["name"]
        if not name:
            session.msg({"alert":_("Name should not be empty.")})
            return

        # sanity checks
        if not (0 < len(name) <= 30):
            # Nickname's length
            string = "\n\r Name can max be 30 characters or fewer."
            session.msg({"alert":string})
            return
        # strip excessive spaces in playername
        nickname = re.sub(r"\s+", " ", name).strip()
        
        charmax = settings.MAX_NR_CHARACTERS if settings.MULTISESSION_MODE > 1 else 1

        if player.db._playable_characters and len(player.db._playable_characters) >= charmax:
            session.msg({"alert":_("You may only create a maximum of %i characters.") % charmax})
            return

        if utils.search_db_data_type("nickname", name, settings.BASE_PLAYER_CHARACTER_TYPECLASS):
            # check if this name already exists.
            session.msg({"alert":_("{rA character named '{w%s{r' already exists.{n") % name})
            return

        try:
            create_character(player, name)
        except Exception, e:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            session.msg({"alert":_("There was an error creating the Player: %s" % e)})
            logger.log_trace()
            return
            
        session.msg({"char_created": True,
                     "char_all": player.get_all_characters()})


class CmdCharDelete(Command):
    """
    Delete a character - this cannot be undone!

    Usage:
        {"cmd":"char_delete",
         "args":{"dbref": <character's dbref>,
                 "password": <player's password>}
        }

    Permanently deletes one of your characters.
    """
    key = "char_delete"
    locks = "cmd:all()"

    def func(self):
        "delete the character"
        player = self.account
        session = self.session
        args = self.args

        if not args:
            self.msg({"alert":_("Please select a character")})
            return
            
        dbref = args["dbref"]
        password = args["password"]
            
        check = player.check_password(password)
        if not check:
            # No password match
            session.msg({"alert":_("Incorrect password.")})
            return

        # use the playable_characters list to search
        match = [char for char in make_iter(player.db._playable_characters) if char.dbref == dbref]
        if not match:
            session.msg({"alert":_("You have no such character to delete.")})
            return
        elif len(match) > 1:
            session.msg({"alert":_("Aborting - there are two characters with the same name. Ask an admin to delete the right one.")})
            return
        else: # one match
            delobj = match[0]
            
            # get new playable characters
            new_characters = [char for char in player.db._playable_characters if char != delobj]
            
            # remove honour
            HONOURS_MAPPER.remove_honour(delobj)
            # remove object
            deleted = delobj.delete()
            
            if not deleted:
                session.msg({"alert":_("Can not delete this character.")})
                return
            
            player.db._playable_characters = new_characters
            session.msg({"char_deleted": True,
                         "char_all": player.get_all_characters()})


class CmdCharAll(Command):
    """
    Get all playable characters of the player.

    Usage:
        {"cmd":"char_all",
         "args":""
        }

    """
    key = "char_all"
    locks = "cmd:all()"
    
    def func(self):
        "delete the character"
        player = self.account
        session = self.session
        
        session.msg({"char_all": player.get_all_characters()})
