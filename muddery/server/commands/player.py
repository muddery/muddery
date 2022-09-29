"""
General account commands usually availabe to all players.
"""

import re, traceback
import base64
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.utils.crypto import RSA
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.builder import create_character
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.commands.command_set import AccountCmd


# Obs - these are all intended to be stored on the Player, and as such,
# use self.player instead of self.caller, just to be sure. Also self.msg()
# is used to make sure returns go to the right session


@AccountCmd.request("delete_account")
async def delete_account(account, args) -> dict:
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
    if not args:
        raise MudderyError(ERR.missing_args, "Syntax error!")

    if "username" not in args:
        raise MudderyError(ERR.missing_args, _("You should input a username."))

    if "password" not in args:
        raise MudderyError(ERR.missing_args, _("You should input a password."))

    username = args["username"]
    username = re.sub(r"\s+", " ", username).strip()

    if SETTINGS.ENABLE_ENCRYPT:
        encrypted = base64.b64decode(args["password"])
        decrypted = RSA.inst().decrypt(encrypted)
        password = decrypted.decode("utf-8")
    else:
        password = args["password"]

    if not password:
        raise MudderyError(ERR.no_authentication, _("Incorrect password."))

    # Set the account with username and password.
    if not await account.check_password(username, password):
        raise MudderyError(ERR.no_authentication, _("Incorrect password."))

    await account.delete_all_characters()
    await account.delete_user(username, password)

    return {
        "name": username
    }


@AccountCmd.request("change_pw")
async def delete_account(account, args) -> dict or None:
    """
    Change the account's password.

    Usage:
        {
            "cmd":"change_pw",
            "args":{
                "current": <current password>,
                "new": <new password>
            }
        }

    Change player's password.
    """
    if "current" not in args:
        raise MudderyError(ERR.missing_args, _("You should input your current password."))

    if "new" not in args:
        raise MudderyError(ERR.missing_args, _("You should input a new password."))

    if SETTINGS.ENABLE_ENCRYPT:
        encrypted = base64.b64decode(args["current"])
        decrypted = RSA.inst().decrypt(encrypted)
        current_password = decrypted.decode("utf-8")
    else:
        current_password = args["current"]

    if not current_password:
        raise MudderyError(ERR.no_authentication, _("Incorrect password."))

    if SETTINGS.ENABLE_ENCRYPT:
        encrypted = base64.b64decode(args["new"])
        decrypted = RSA.inst().decrypt(encrypted)
        new_password = decrypted.decode("utf-8")
    else:
        new_password = args["new"]

    if not new_password:
        raise MudderyError(ERR.missing_args, _("You should input a new password."))

    await account.change_password(new_password)

    return


@AccountCmd.request("puppet")
async def puppet(account, args) -> dict:
    """
    Control an object you have permission to puppet

    Usage:
        {
            "cmd":"puppet",
            "args":<object's id>
        }

    Puppet a given Character.
    """
    if not args:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))

    puppet_id = args
    char_all = await account.get_all_characters()
    if puppet_id not in char_all:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))

    try:
        return await account.puppet_character(puppet_id)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))


@AccountCmd.request("puppet_name")
async def puppet_name(account, args) -> dict or None:
    """
    Control an object you have permission to puppet

    Usage:
        {
            "cmd": "puppet_name",
            "args": <character's name>
        }

    Puppet a given Character.
    """
    if not args:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))

    puppet_name = args
    char_all = await account.get_all_nicknames()
    puppet_id = None
    for char_info in char_all:
        if puppet_name == char_info["name"]:
            puppet_id = char_info["id"]
            break

    if puppet_id is None:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))

    try:
        return await account.puppet_character(puppet_id)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))


@AccountCmd.request("unpuppet")
async def unpuppet(account, args) -> dict or None:
    """
    Stop puppeting the character.

    Usage:
        {
            "cmd": "unpuppet",
            "args": ""
        }
    """
    try:
        await account.unpuppet_character()
    except Exception as e:
        logger.log_err("Unpuppet error: %s" % e)

    return


@AccountCmd.request("char_create")
async def char_create(account, args) -> dict or None:
    """
    Create a new character

    Usage:
        {
            "cmd":"char_create",
            "args": {
                "name": <character's name>
            }
        }

    Create a new character with a name.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should give the character a name."))

    name = args["name"]
    if not name:
        raise MudderyError(ERR.invalid_input, _("Name should not be empty."))

    # sanity checks
    if not (0 < len(name) <= 30):
        # Nickname's length
        raise MudderyError(ERR.invalid_input, _("\n\r Name can max be 30 characters or fewer."))

    # check total characters number
    char_all = await account.get_all_characters()
    if len(char_all) >= SETTINGS.MAX_PLAYER_CHARACTERS:
        msg = _("You may only create a maximum of %i characters.") % SETTINGS.MAX_PLAYER_CHARACTERS
        raise MudderyError(ERR.invalid_input, msg)

    # strip excessive spaces in playername
    nickname = re.sub(r"\s+", " ", name).strip()

    try:
        await CharacterInfo.inst().get_char_id(nickname)
        # check if this name already exists.
        raise MudderyError(ERR.invalid_input, _("{RA character named '{r%s{R' already exists.{n") % name)
    except KeyError:
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
        logger.log_trace()
        raise MudderyError(ERR.unknown, _("There was an error creating the Player: %s" % e))

    return


@AccountCmd.request("char_delete")
async def char_delete(account, args) -> dict or None:
    """
    Delete a character - this cannot be undone!

    Usage:
        {"cmd":"char_delete",
         "args":{"id": <character's id>}
        }

    Permanently deletes one of your characters.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("Please select a character"))

    char_id = args["id"]

    try:
        await account.delete_character(char_id)
    except Exception as e:
        logger.log_err("Can not delete character %s: %s")
        raise MudderyError(ERR.unknown, _("Can not delete this character."))

    return


@AccountCmd.request("char_delete_pw")
async def char_delete_pw(account, args) -> dict or None:
    """
    Delete a character - this cannot be undone!

    Usage:
        {
            "cmd": "char_delete",
            "args": {
                "id": <character's id>,
                "password": <player's password>
            }
        }

    Permanently deletes one of your characters.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("Please select a character"))

    if "id" not in args:
        raise MudderyError(ERR.missing_args, _("Please select a character"))

    if "password" not in args:
        raise MudderyError(ERR.missing_args, _("You should input your password."))

    char_id = args["id"]

    if SETTINGS.ENABLE_ENCRYPT:
        encrypted = base64.b64decode(args["password"])
        decrypted = RSA.inst().decrypt(encrypted)
        password = decrypted.decode("utf-8")
    else:
        password = args["password"]

    if not password:
        raise MudderyError(ERR.missing_args, _("You should input your password."))

    check = await account.check_password(password)
    if not check:
        # No password match
        raise MudderyError(ERR.no_authentication, _("Incorrect password."))

    try:
        await account.delete_character(char_id)
    except Exception as e:
        logger.log_err("Can not delete character %s: %s")
        raise MudderyError(ERR.unknown, _("Can not delete this character."))

    return


@AccountCmd.request("char_all")
async def func(account, args):
    """
    Get all playable characters of the player.

    Usage:
        {"cmd":"char_all",
         "args":""
        }

    """
    return {
        "char_all": await account.get_all_nicknames(),
    }


@AccountCmd.request("logout")
async def logout(session, args):
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
    return await session.logout()
