"""
General account commands usually availabe to all players.
"""

import re, traceback
import base64
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.utils.crypto import RSA
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.builder import create_character
from muddery.server.database.gamedata.character_info import CharacterInfo


# Obs - these are all intended to be stored on the Player, and as such,
# use self.player instead of self.caller, just to be sure. Also self.msg()
# is used to make sure returns go to the right session


class CmdDeleteAccount(BaseCommand):
    """
    Delete a player's account.

    Usage:
        {
            "cmd":"delete_account",
            "args":{
                "playername":<playername>,
                "password":<password>,
            }
        }

    args:
        connect: (boolean)connect after created
    """
    key = "delete_account"

    @classmethod
    async def func(cls, account, args):
        "Do checks, create account and login."
        if not args:
            await account.msg({"alert": _("Syntax error!")})
            return

        if "username" not in args:
            await account.msg({"alert": _("You should input a username.")})
            return

        if "password" not in args:
            await account.msg({"alert": _("You should input a password.")})
            return

        username = args["username"]
        username = re.sub(r"\s+", " ", username).strip()

        if SETTINGS.ENABLE_ENCRYPT:
            encrypted = base64.b64decode(args["password"])
            decrypted = RSA.inst().decrypt(encrypted)
            password = decrypted.decode("utf-8")
        else:
            password = args["password"]

        if not password:
            await account.msg({"alert": _("You should input a password.")})
            return

        # Set the account with username and password.
        if not await account.check_password(username, password):
            await account.msg({"alert": _("Incorrect password.")})
            return

        await account.delete_all_characters()
        await account.delete_user(username, password)


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
    async def func(cls, account, args):
        # we are quitting the last available session
        await account.msg({
            "msg": "{RQuitting{n. Hope to see you again, soon.",
            "logout": True,
        })
        await account.disconnect()


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
    async def func(cls, account, args):
        "hook function"
        if "current" not in args:
            await account.msg({"alert": _("You should input your current password.")})
            return

        if "new" not in args:
            await account.msg({"alert": _("You should input a new password.")})
            return

        if SETTINGS.ENABLE_ENCRYPT:
            encrypted = base64.b64decode(args["current"])
            decrypted = RSA.inst().decrypt(encrypted)
            current_password = decrypted.decode("utf-8")
        else:
            current_password = args["current"]

        if not current_password:
            await account.msg({"alert": _("You should input your current password.")})
            return

        if SETTINGS.ENABLE_ENCRYPT:
            encrypted = base64.b64decode(args["new"])
            decrypted = RSA.inst().decrypt(encrypted)
            new_password = decrypted.decode("utf-8")
        else:
            new_password = args["new"]

        if not new_password:
            await account.msg({"alert": _("You should input a new password.")})
            return

        await account.change_password(current_password, new_password)


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
    async def func(cls, account, args):
        """
        Main puppet method
        """
        if not args:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return

        puppet_id = args
        char_all = await account.get_all_characters()
        if puppet_id not in char_all:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return

        try:
            await account.puppet_character(puppet_id)
        except Exception as e:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return


class CmdPuppetName(BaseCommand):
    """
    Control an object you have permission to puppet

    Usage:
        {
            "cmd":"puppet",
            "args":<character's name>
        }

    Puppet a given Character.

    This will attempt to "become" a different character assuming you have
    the right to do so. Note that it's the PLAYER character that puppets
    characters/objects and which needs to have the correct permission!

    """
    key = "puppet_name"

    @classmethod
    async def func(cls, account, args):
        """
        Main puppet method
        """
        if not args:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return

        puppet_name = args
        char_all = await account.get_all_nicknames()
        puppet_id = None
        for char_info in char_all:
            if puppet_name == char_info["name"]:
                puppet_id = char_info["id"]
                break

        if puppet_id is None:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return

        try:
            await account.puppet_character(puppet_id)
        except Exception as e:
            await account.msg({"alert": _("That is not a valid character choice.")})
            return


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
    async def func(cls, account, args):
        # disconnect
        try:
            await account.unpuppet_character()
            await account.msg({"unpuppet": True})
        except RuntimeError as e:
            await account.msg({"alert":_("Could not unpuppet: %s" % e)})
            return
        except Exception as e:
            logger.log_err("Could not unpuppet: %s" % e)
            return


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
    async def func(cls, account, args):
        "create the new character"
        if not args:
            await account.msg({"alert":_("You should give the character a name.")})
            return
        
        name = args["name"]
        if not name:
            await account.msg({"alert":_("Name should not be empty.")})
            return

        # sanity checks
        if not (0 < len(name) <= 30):
            # Nickname's length
            string = "\n\r Name can max be 30 characters or fewer."
            await account.msg({"alert":string})
            return

        # check total characters number
        char_all = await account.get_all_characters()
        if len(char_all) >= SETTINGS.MAX_PLAYER_CHARACTERS:
            await account.msg({"alert": _("You may only create a maximum of %i characters.") % SETTINGS.MAX_PLAYER_CHARACTERS})
            return

        # strip excessive spaces in playername
        nickname = re.sub(r"\s+", " ", name).strip()

        try:
            await CharacterInfo.inst().get_char_id(nickname)
            # check if this name already exists.
            await account.msg({"alert":_("{RA character named '{r%s{R' already exists.{n") % name})
            return
        except:
            pass

        try:
            if SETTINGS.TEST_MODE:
                await create_character(
                    account,
                    name,
                    element_type=SETTINGS.PLAYER_CHARACTER_TYPE_TEST_MODE,
                    character_key=SETTINGS.PLAYER_CHARACTER_KEY_TEST_MODE,
                )
            else:
                await create_character(account, name)
        except Exception as e:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't,
            # we won't see any errors at all.
            await account.msg({"alert":_("There was an error creating the Player: %s" % e)})
            logger.log_trace()
            return

        await account.msg({
            "char_created": True,
            "char_all": await account.get_all_nicknames(),
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
    async def func(cls, account, args):
        "delete the character"
        if not args:
            await account.msg({"alert":_("Please select a character")})
            return

        char_id = args["id"]

        try:
            await account.delete_character(char_id)
        except Exception as e:
            logger.log_err("Can not delete character %s: %s")
            await account.msg({"alert": _("You can not delete this character.")})
            return

        await account.msg({
            "char_deleted": True,
            "char_all": await account.get_all_nicknames(),
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
    async def func(cls, account, args):
        "delete the character"
        if not args:
            await account.msg({"alert": _("Please select a character")})
            return

        if "id" not in args:
            await account.msg({"alert": _("Please select a character")})
            return

        if "password" not in args:
            await account.msg({"alert": _("You should input your password.")})
            return

        char_id = args["id"]

        if SETTINGS.ENABLE_ENCRYPT:
            encrypted = base64.b64decode(args["password"])
            decrypted = RSA.inst().decrypt(encrypted)
            password = decrypted.decode("utf-8")
        else:
            password = args["password"]

        if not password:
            await account.msg({"alert": _("You should input your password.")})
            return

        check = await account.check_password(password)
        if not check:
            # No password match
            await account.msg({"alert":_("Incorrect password.")})
            return

        try:
            await account.delete_character(char_id)
        except Exception as e:
            logger.log_err("Can not delete character %s: %s")
            await account.msg({"alert": _("You can not delete this character.")})
            return

        await account.msg({
            "char_deleted": True,
            "char_all": await account.get_all_nicknames(),
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
    async def func(cls, account, args):
        "delete the character"
        await account.msg({"char_all": account.get_all_nicknames()})
