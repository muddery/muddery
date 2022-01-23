"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.
"""

import traceback
import datetime
import asyncio
from muddery.server.settings import SETTINGS
from muddery.server.utils.password import hash_password, check_password, make_salt
from muddery.server.database.gamedata.accounts import Accounts
from muddery.server.database.gamedata.server_bans import ServerBans
from muddery.server.database.gamedata.system_data import SystemData
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.character_location import CharacterLocation
from muddery.server.database.gamedata.character_inventory import CharacterInventory
from muddery.server.database.gamedata.character_equipments import CharacterEquipments
from muddery.server.database.gamedata.character_quests import CharacterQuests
from muddery.server.database.gamedata.character_skills import CharacterSkills
from muddery.server.database.gamedata.character_combat import CharacterCombat
from muddery.server.database.gamedata.honours_mapper import HonoursMapper
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.server import Server
from muddery.server.utils.game_settings import GameSettings
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.logger import logger


_SESSIONS = None


class MudderyAccount(BaseElement):
    """
    The character not controlled by players.

    States:
        shops
    """
    element_type = "ACCOUNT"
    element_name = "Account"
    model_name = ""

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyAccount, self).__init__()

        self.username = None
        self.id = None
        self.type = ""
        self.session = None
        self.puppet_obj = None

    def __str__(self):
        """
        Output self as a string
        """
        output = str(self.get_id())
        if self.puppet_obj:
            output += "-" + str(self.puppet_obj)
        return output

    async def new_user(self, username, raw_password, type):
        # Create a new account with the username and password.
        if await Accounts.inst().has(username):
            raise MudderyError(ERR.invalid_input, _("Sorry, there is already a player with the name '%s'.") % username)

        # Check name bans
        current_time = datetime.datetime.now()
        try:
            finish_time = await ServerBans.inst().get_ban_time("USERNAME", username)
            if current_time <= finish_time:
                # This username is banned.
                raise MudderyError(ERR.no_authentication, _("You have been banned."))
        except KeyError:
            pass

        if len(raw_password) < 6:
            raise MudderyError(ERR.invalid_input, _("The password is too simple."))

        salt = make_salt()
        password = hash_password(raw_password, salt)

        # Get a new player character id.
        account_id = await SystemData.inst().load("last_account_id", 0, for_update=True)
        account_id += 1
        await SystemData.inst().save("last_account_id", account_id)

        await Accounts.inst().add(username, password, salt, account_id, type)
        self.username = username
        self.id = account_id
        self.type = type

    async def delete_user(self, username, raw_password):
        """
        Delete a user.
        :param username:
        :param raw_password:
        :return:
        """
        if not await self.check_password(username, raw_password):
            # Password not match.
            raise MudderyError(ERR.no_authentication, _("Incorrect username or password."))

        await Accounts.inst().remove(username)

    async def set_user(self, username, raw_password):
        # Match account name and check password
        if not await self.check_password(username, raw_password):
            # Password not match.
            raise MudderyError(ERR.no_authentication, _("Incorrect username or password."))

        # Check name bans
        try:
            finish_time = await ServerBans.inst().get_ban_time("USERNAME", username)
            current_time = datetime.datetime.now()
            if current_time <= finish_time:
                # This username is banned.
                raise MudderyError(ERR.no_authentication, _("You have been banned."))
        except KeyError:
            pass

        info = await Accounts.inst().get_info(username)
        self.username = username
        self.id = info["id"]
        self.type = info["type"]

    def is_valid(self):
        """
        Checkes if this account is valid.
        """
        return self.id is not None

    def get_id(self):
        """
        Get the account's id.
        :return:
        """
        return self.id

    def get_session_id(self):
        if self.session:
            return self.session.uid

    async def at_post_login(self, session):
        """
        Called at the end of the login process.
        """
        self.session = session

        await asyncio.wait([
            asyncio.create_task(Accounts.inst().update_login_time(self.username)),

            # Inform the client that we logged in first.
            asyncio.create_task(session.msg([
                {
                    "login": {
                        "name": self.username,
                        "id": self.get_id(),
                    },
                },
                {
                    "char_all": await self.get_all_nicknames(),
                    "max_char": SETTINGS.MAX_PLAYER_CHARACTERS
                },
            ])),
        ])

    async def at_pre_logout(self):
        """
        Called before the logout process.
        """
        if self.puppet_obj:
            await self.unpuppet_character()

    async def get_all_characters(self):
        """
        Get this player's all playable characters.
        """
        return await AccountCharacters.inst().get_account_characters(self.id)

    async def get_all_nicknames(self):
        """
        Get this player's all playable characters' nicknames.
        """
        char_all = await self.get_all_characters()
        return [{"name": await CharacterInfo.inst().get_nickname(char_id), "id": char_id} for char_id in char_all]

    async def msg(self, data, delay=True):
        """
        Element -> User
        This is the main route for sending data back to the user from the
        server.

        Args:
            text (str, optional): text data to send
            session (Session or list, optional): Session object or a list of
                Sessions to receive this send. If given, overrules the
                default send behavior for the current
                MULTISESSION_MODE.
            options (list): Protocol-specific options. Passed on to the protocol.
        Kwargs:
            any (dict): All other keywords are passed on to the protocol.

        """
        # session relay
        if self.session:
            await self.session.msg(data, delay)

    async def puppet_character(self, char_db_id):
        """
        Use the given session to control (puppet) the given object (usually
        a Character type).

        Args:
            session (Session): session to use for puppeting
            char_db_id (Int): the character's db id
            char_key (String): the character's key

        Raises:
            RuntimeError: If puppeting is not possible, the
                `exception.msg` will contain the reason.
        """
        # safety checks
        if not char_db_id:
            raise RuntimeError("Object not found")
        if not self.session:
            raise RuntimeError("Session not found")

        current_obj = self.puppet_obj
        if current_obj and current_obj.get_db_id() == char_db_id:
            # already puppeting this object
            await self.msg("You are already puppeting this object.")
            return

        self.puppet_obj = None

        # if we get to this point the character is ready to puppet or it
        # was left with a lingering account/session reference from an unclean
        # server kill or similar

        # Find the character to puppet.
        try:
            if self.type == "STAFF":
                char_type = SETTINGS.STAFF_CHARACTER_ELEMENT_TYPE
                char_key = await GameSettings.inst().get("default_staff_character_key")
            else:
                char_info = await CharacterInfo.inst().get(char_db_id)
                char_type = char_info["element_type"]
                char_key = char_info["element_key"]

            new_char = ELEMENT(char_type)()
            new_char.set_db_id(char_db_id)

            # do the connection
            new_char.set_account(self)
            await new_char.setup_element(char_key)
        except Exception as e:
            traceback.print_exc()
            await self.msg({"alert": _("That is not a valid character choice.")})
            return

        # Send puppet info to the client first.
        await self.msg({
            "puppet": {
                "id": new_char.get_id(),
                "name": new_char.get_name(),
                "icon": getattr(new_char, "icon", None),
            }
        })

        # Set location
        try:
            location_key = await CharacterLocation.inst().load(char_db_id)
            location = Server.world.get_room(location_key)
            await new_char.move_to(location)
        except KeyError:
            pass

        self.puppet_obj = new_char
        self.session.puid = char_db_id

        # add the character to the world
        Server.world.on_char_puppet(new_char)

        # final hook
        await new_char.at_post_puppet()

    async def unpuppet_character(self):
        """
        Disengage control over an object.

        Raises:
            RuntimeError With message about error.

        """
        obj = self.puppet_obj
        if obj:
            await obj.at_pre_unpuppet()

            Server.world.on_char_unpuppet(obj)

            # Just to be sure we're always clear.
            self.puppet_obj = None

        if self.session:
            self.session.puid = None

    def get_puppet_obj(self):
        """
        Get the object current controlling.
        """
        return self.puppet_obj

    async def delete_character(self, char_db_id):
        """
        Delete an character.

        :param char_db_id:
        :return:
        """
        # use the playable_characters list to search
        characters = await AccountCharacters.inst().get_account_characters(self.id)
        if char_db_id not in characters:
            raise KeyError("Can not find the character.")

        await self.unpuppet_character()

        # delete all character data.
        await asyncio.wait([
            asyncio.create_task(AccountCharacters.inst().remove_character(self.id, char_db_id)),
            asyncio.create_task(CharacterInfo.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterLocation.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterInventory.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterEquipments.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterQuests.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterSkills.inst().remove_character(char_db_id)),
            asyncio.create_task(CharacterCombat.inst().remove_character(char_db_id)),
            asyncio.create_task(HonoursMapper.inst().remove_character(char_db_id)),
        ])

    async def delete_all_characters(self):
        """
        Delete an character.

        :param char_db_id:
        :return:
        """
        await self.unpuppet_character()

        all_characters = await self.get_all_characters()
        awaits = []
        for char_db_id in all_characters:
            # delete all character data.
            awaits.append(asyncio.create_task(AccountCharacters.inst().remove_character(self.id, char_db_id)))
            awaits.append(asyncio.create_task(CharacterInfo.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterLocation.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterInventory.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterEquipments.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterQuests.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterSkills.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(CharacterCombat.inst().remove_character(char_db_id)))
            awaits.append(asyncio.create_task(HonoursMapper.inst().remove_character(char_db_id)))

        if awaits:
            await asyncio.wait(awaits)

    def at_cmdset_get(self):
        pass

    async def check_password(self, username, raw_password):
        """
        Check if the password is correct.
        """
        try:
            password, salt = await Accounts.inst().get_password(username)
        except KeyError:
            # Wrong username.
            return False

        return check_password(raw_password, password, salt)

    async def change_password(self, current_password, new_password):
        """
        Change the account's password.
        """
        if not self.check_password(self.username, current_password):
            await self.msg({"alert":_("Incorrect password.")})
            return

        salt = make_salt()
        password = hash_password(new_password, salt)
        await Accounts.inst().set_password(self.username, password, salt)

        await self.msg({
            "alert":_("Password changed."),
            "pw_changed": True
        })

    async def disconnect(self, reason):
        """
        Disconnect the session
        """
        if self.session:
            await self.session.disconnect(reason)
            self.session = None
