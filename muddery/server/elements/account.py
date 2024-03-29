"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.
"""

import traceback
import datetime
from muddery.server.settings import SETTINGS
from muddery.common.utils.password import hash_password, check_password, make_salt
from muddery.server.database.worlddata.equipment_positions import EquipmentPositions
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.database.gamedata.accounts import Accounts
from muddery.server.database.gamedata.server_bans import ServerBans
from muddery.server.database.gamedata.system_data import SystemData
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.character_location import CharacterLocation
from muddery.server.database.gamedata.character_revealed_map import CharacterRevealedMap
from muddery.server.database.gamedata.character_inventory import CharacterInventory
from muddery.server.database.gamedata.character_equipments import CharacterEquipments
from muddery.server.database.gamedata.character_quests import CharacterQuests
from muddery.server.database.gamedata.character_finished_quests import CharacterFinishedQuests
from muddery.server.database.gamedata.character_skills import CharacterSkills
from muddery.server.database.gamedata.character_combat import CharacterCombat
from muddery.server.database.gamedata.character_closed_events import CharacterClosedEvents
from muddery.server.database.gamedata.character_quest_objectives import CharacterQuestObjectives
from muddery.server.database.gamedata.character_relationships import CharacterRelationships
from muddery.server.database.gamedata.object_storage import CharacterObjectStorage
from muddery.server.database.gamedata.honours_mapper import HonoursMapper
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.server import Server
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.server.utils.game_settings import GameSettings
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.common.utils.utils import async_wait, async_gather


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
            raise MudderyError(ERR.account_not_available)

        # Check name bans
        current_time = datetime.datetime.now()
        try:
            finish_time = await ServerBans.inst().get_ban_time("USERNAME", username)
            if current_time <= finish_time:
                # This username is banned.
                raise MudderyError(ERR.no_permission)
        except KeyError:
            pass

        if len(raw_password) < 6:
            raise MudderyError(ERR.password_too_simple)

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
            raise MudderyError(ERR.no_authentication)

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
                raise MudderyError(ERR.no_permission)
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

    async def login(self, session) -> dict:
        """
        Called at the end of the login process.
        """
        self.session = session

        await Accounts.inst().update_login_time(self.username)

        # return login messages
        return {
            "name": self.username,
            "id": self.get_id(),
        }

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
        if char_all:
            nicknames = await async_gather([CharacterInfo.inst().get_nickname(c) for c in char_all])
        else:
            nicknames = []
        return [{"name": nicknames[index], "id": char_id} for index, char_id in enumerate(char_all)]

    def msg(self, data):
        """
        Element -> User
        This is the main route for sending data back to the user from the
        server.

        Args:
            data (dict): data to send
        """
        # session relay
        if self.session:
            self.session.msg(data)

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
            raise MudderyError(ERR.invalid_input, _("You have already puppet this object."))

        self.puppet_obj = None

        # if we get to this point the character is ready to puppet or it
        # was left with a lingering account/session reference from an unclean
        # server kill or similar

        # Find the character to puppet.
        try:
            new_char = None

            # Check if the character is in a combat.
            combat_id = await CharacterCombat.inst().load(char_db_id, None)
            if combat_id is not None:
                # Get the character from the combat.
                combat = COMBAT_HANDLER.get_combat(combat_id)
                if combat:
                    new_char = combat.get_character(char_db_id)

            if new_char:
                new_char.puppet(self)
            else:
                # Create a new object.
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
                new_char.puppet(self)
                await new_char.setup_element(char_key)
        except Exception as e:
            raise MudderyError(ERR.invalid_input, _("That is not a valid character choice."))

        # Set location
        move_results = {}
        try:
            location_key = await CharacterLocation.inst().load(char_db_id)
            location = Server.world.get_room(location_key)
            move_results = await new_char.move_to(location)
        except KeyError:
            pass

        self.puppet_obj = new_char
        self.session.puid = char_db_id

        # add the character to the world
        Server.world.on_char_puppet(new_char)

        state, last_combat = await async_gather([
            new_char.get_state(),
            new_char.get_last_combat(),
        ])

        honour_settings = HonourSettings.get_first_data()
        records = EquipmentPositions.all()
        equipment_pos = [{
            "key": r.key,
            "name": r.name,
            "desc": r.desc,
        } for r in records]

        # Send puppet info to the client first.
        character_info = {
            "id": new_char.get_id(),
            "name": new_char.get_name(),
            "icon": getattr(new_char, "icon", None),
            "state": state,
            "location": new_char.get_location_info(),
            "look_around": new_char.look_around(),
            "revealed_maps": new_char.get_revealed_maps(),
            "channels": new_char.get_available_channels(),
            "equipment_pos": equipment_pos,
            "min_honour_level": honour_settings.min_honour_level,
        }

        if move_results and "at_arrive" in move_results:
            character_info["at_arrive"] = move_results["at_arrive"]

        if self.type == "STAFF":
            character_info["is_staff"] = True

        if last_combat:
            character_info["last_combat"] = last_combat

        return character_info

    async def unpuppet_character(self):
        """
        Disengage control over an object.

        Raises:
            RuntimeError With message about error.

        """
        obj = self.puppet_obj
        if obj:
            await obj.unpuppet()

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

        # character object's data
        object_states = ObjectStatesHandler(char_db_id, CharacterObjectStorage)

        # delete all character data.
        await async_wait([
            object_states.clear(),
            AccountCharacters.inst().remove_character(self.id, char_db_id),
            CharacterInfo.inst().remove_character(char_db_id),
            CharacterLocation.inst().remove_character(char_db_id),
            CharacterRevealedMap.inst().remove_character(char_db_id),
            CharacterInventory.inst().remove_character(char_db_id),
            CharacterEquipments.inst().remove_character(char_db_id),
            CharacterQuests.inst().remove_character(char_db_id),
            CharacterFinishedQuests.inst().remove_character(char_db_id),
            CharacterSkills.inst().remove_character(char_db_id),
            CharacterCombat.inst().remove_character(char_db_id),
            CharacterClosedEvents.inst().remove_character(char_db_id),
            CharacterQuestObjectives.inst().remove_character(char_db_id),
            CharacterRelationships.inst().remove_character(char_db_id),
            HonoursMapper.inst().remove_character(char_db_id),
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
            # character object's data
            object_states = ObjectStatesHandler(char_db_id, CharacterObjectStorage)

            # delete all character data.
            awaits.extend([
                object_states.clear(),
                AccountCharacters.inst().remove_character(self.id, char_db_id),
                CharacterInfo.inst().remove_character(char_db_id),
                CharacterLocation.inst().remove_character(char_db_id),
                CharacterRevealedMap.inst().remove_character(char_db_id),
                CharacterInventory.inst().remove_character(char_db_id),
                CharacterEquipments.inst().remove_character(char_db_id),
                CharacterQuests.inst().remove_character(char_db_id),
                CharacterFinishedQuests.inst().remove_character(char_db_id),
                CharacterSkills.inst().remove_character(char_db_id),
                CharacterCombat.inst().remove_character(char_db_id),
                CharacterClosedEvents.inst().remove_character(char_db_id),
                CharacterQuestObjectives.inst().remove_character(char_db_id),
                CharacterRelationships.inst().remove_character(char_db_id),
                HonoursMapper.inst().remove_character(char_db_id),
            ])

        if awaits:
            await async_wait(awaits)

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

    async def change_password(self, new_password):
        """
        Change the account's password.
        """
        salt = make_salt()
        password = hash_password(new_password, salt)
        await Accounts.inst().set_password(self.username, password, salt)
        return

    async def logout(self):
        """
        Logout the session
        """
        if self.session:
            await self.session.logout()
            self.session = None
