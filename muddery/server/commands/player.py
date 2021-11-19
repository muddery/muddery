"""
This is adapt from evennia/evennia/commands/default/player.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

"""

import re, traceback
from django.conf import settings
from muddery.server.utils import logger
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.builder import create_character
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.utils.game_settings import GAME_SETTINGS


# Obs - these are all intended to be stored on the Player, and as such,
# use self.player instead of self.caller, just to be sure. Also self.msg()
# is used to make sure returns go to the right session


class CmdQuit(BaseCommand):
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

    @classmethod
    def func(cls, account, args):
        # we are quitting the last available session
        account.disconnect()
        account.msg({
            "msg": "{RQuitting{n. Hope to see you again, soon.",
            "logout": ""
        })


class CmdChangePassword(BaseCommand):
    """
    Quit the game.

    Usage:
        {"cmd":"change_pw",
         "args":{"current": <current password>,
                 "new": <new password>
                }
        }

    Change player's password.
    """
    key = "change_pw"

    @classmethod
    def func(cls, account, args):
        "hook function"
        current_password = args["current"]
        new_password = args["new"]

        account.change_password(current_password, new_password)


class CmdPuppet(BaseCommand):
    """
    Control an object you have permission to puppet

    Usage:
        {"cmd":"puppet",
         "args":<object's id>
        }

    Puppet a given Character.

    This will attempt to "become" a different character assuming you have
    the right to do so. Note that it's the PLAYER character that puppets
    characters/objects and which needs to have the correct permission!

    """
    key = "puppet"

    @classmethod
    def func(cls, account, args):
        """
        Main puppet method
        """
        if not args:
            account.msg({"alert": _("That is not a valid character choice.")})
            return

        char_id = args
        char_all = account.get_all_characters()
        if char_id not in char_all:
            account.msg({"alert": _("That is not a valid character choice.")})
            return

        try:
            account.puppet_object(char_id)
        except Exception as e:
            traceback.print_exc()
            account.msg({"alert": _("That is not a valid character choice.")})


class CmdUnpuppet(BaseCommand):
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

    @classmethod
    def func(cls, account, args):
        # disconnect
        try:
            account.unpuppet_object()
            account.msg({"unpuppet": True})
        except RuntimeError as e:
            account.msg({"alert":_("Could not unpuppet: %s" % e)})
        except Exception as e:
            logger.log_err("Could not unpuppet: %s" % e)


class CmdCharCreate(BaseCommand):
    """
    Create a new character

    Usage:
        {"cmd":"char_create",
         "args":{"name": <character's name>}
        }

    Create a new character with a name.
    """
    key = "char_create"

    @classmethod
    def func(cls, account, args):
        "create the new character"
        if not args:
            account.msg({"alert":_("You should give the character a name.")})
            return
        
        name = args["name"]
        if not name:
            account.msg({"alert":_("Name should not be empty.")})
            return

        # sanity checks
        if not (0 < len(name) <= 30):
            # Nickname's length
            string = "\n\r Name can max be 30 characters or fewer."
            account.msg({"alert":string})
            return

        # check total characters number
        char_all = account.get_all_characters()
        if len(char_all) >= settings.MAX_NR_CHARACTERS:
            account.msg({"alert": _("You may only create a maximum of %i characters.") % settings.MAX_NR_CHARACTERS})
            return

        # strip excessive spaces in playername
        nickname = re.sub(r"\s+", " ", name).strip()

        try:
            CharacterInfo.get_char_id(nickname)
            # check if this name already exists.
            account.msg({"alert":_("{RA character named '{r%s{R' already exists.{n") % name})
            return
        except:
            pass

        try:
            create_character(account, name)
        except Exception as e:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            account.msg({"alert":_("There was an error creating the Player: %s" % e)})
            logger.log_trace()
            return

        account.msg({
            "char_created": True,
            "char_all": account.get_all_nicknames(),
        })


class CmdCharDelete(BaseCommand):
    """
    Delete a character - this cannot be undone!

    Usage:
        {"cmd":"char_delete",
         "args":{"id": <character's id>}
        }

    Permanently deletes one of your characters.
    """
    key = "char_delete"

    @classmethod
    def func(cls, account, args):
        "delete the character"
        if not args:
            account.msg({"alert":_("Please select a character")})
            return

        char_id = args["id"]

        try:
            account.delete_character(char_id)
        except Exception as e:
            logger.log_err("Can not delete character %s: %s")
            account.msg({"alert": _("You can not delete this character.")})
            return

        account.msg({
            "char_deleted": True,
            "char_all": account.get_all_nicknames(),
        })


class CmdCharDeleteWithPW(BaseCommand):
    """
    Delete a character - this cannot be undone!

    Usage:
        {"cmd":"char_delete",
         "args":{"id": <character's id>,
                 "password": <player's password>}
        }

    Permanently deletes one of your characters.
    """
    key = "char_delete"

    @classmethod
    def func(cls, account, args):
        "delete the character"
        if not args:
            account.msg({"alert":_("Please select a character")})
            return
            
        char_id = args["id"]
        password = args["password"]
            
        check = account.check_password(password)
        if not check:
            # No password match
            account.msg({"alert":_("Incorrect password.")})
            return

        try:
            account.delete_character(char_id)
        except Exception as e:
            logger.log_err("Can not delete character %s: %s")
            account.msg({"alert": _("You can not delete this character.")})
            return

        account.msg({
            "char_deleted": True,
            "char_all": account.get_all_nicknames(),
        })


class CmdCharAll(BaseCommand):
    """
    Get all playable characters of the player.

    Usage:
        {"cmd":"char_all",
         "args":""
        }

    """
    key = "char_all"

    @classmethod
    def func(cls, account, args):
        "delete the character"
        char_all = account.get_all_characters()
        account.msg({
            "char_all": [{"name": data["nickname"], "id": char_id} for char_id, data in char_all.items()],
        })
