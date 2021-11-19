"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.
"""

import traceback
import datetime
from django.conf import settings
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
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
from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.server import Server
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils import logger


_SESSIONS = None


class MudderyAccount(BaseElement):
    """
    The character not controlled by players.

    States:
        shops
    """
    element_type = "ACCOUNT"
    element_name = _("Account", "elements")
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

    def new_user(self, username, password, type, session):
        # Create a new account with the username and password.
        if Accounts.has(username):
            raise MudderyError(ERR.invalid_input, _("Sorry, there is already a player with the name '%s'.") % username)

        # Check name bans
        current_time = datetime.datetime.now()
        try:
            finish_time = ServerBans.get_ban_time("USERNAME", username)
            if current_time <= finish_time:
                # This username is banned.
                raise MudderyError(ERR.no_authentication, _("You have been banned."))
        except KeyError:
            pass

        if not is_password_usable(password):
            raise MudderyError(ERR.invalid_input, _("The password is too simple."))

        raw_password = make_password(password)

        # Get a new player character id.
        # TODO: load for update
        account_id = SystemData.load("last_account_id", 0)
        account_id += 1
        SystemData.save("last_account_id", account_id)

        Accounts.add(username, raw_password, account_id, type)
        self.username = username
        self.id = account_id
        self.type = type
        self.session = session

    def set_user(self, username, password, session):
        # Match account name and check password
        if not self.check_password(username, password):
            # Password not match.
            raise MudderyError(ERR.no_authentication, _("Incorrect username or password."))

        # Check name bans
        try:
            finish_time = ServerBans.get_ban_time("USERNAME", username)
            current_time = datetime.datetime.now()
            if current_time <= finish_time:
                # This username is banned.
                raise MudderyError(ERR.no_authentication, _("You have been banned."))
        except KeyError:
            pass

        info = Accounts.get_info(username)
        self.username = username
        self.id = info["id"]
        self.type = info["type"]
        self.session = session

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

    def at_post_login(self, session=None, **kwargs):
        """
        Called at the end of the login process, just before letting
        the account loose.

        Args:
            session (Session, optional): Session logging in, if any.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            This is called *before* an eventual Character's
            `at_post_login` hook. By default it is used to set up
            auto-puppeting based on `MULTISESSION_MODE`.

        """
        Accounts.update_login_time(self.username)

        # inform the client that we logged in through an OOB message
        if session:
            session.msg(logged_in={})

            session.msg({
                "char_all": self.get_all_nicknames(),
                "max_char": settings.MAX_NR_CHARACTERS
            })

    def get_all_characters(self):
        """
        Get this player's all playable characters.
        """
        return AccountCharacters.get_account_characters(self.id)

    def get_all_nicknames(self):
        """
        Get this player's all playable characters' nicknames.
        """
        char_all = self.get_all_characters()
        return [{"name": CharacterInfo.get_nickname(char_id), "id": char_id} for char_id in char_all]

    def msg(self, text):
        """
        Evennia -> User
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
        logger.log_info("Account %s send message: %s" % (self.get_id(), text))
        if self.session:
            self.session.data_out(text=text)

    def puppet_object(self, char_db_id):
        """
        Use the given session to control (puppet) the given object (usually
        a Character type).

        Args:
            session (Session): session to use for puppeting
            char_db_id (Int): the character's db id

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
            self.msg("You are already puppeting this object.")
            return

        self.puppet_obj = None

        # if we get to this point the character is ready to puppet or it
        # was left with a lingering account/session reference from an unclean
        # server kill or similar

        # Find the character to puppet.
        try:
            if self.type == "STAFF":
                new_char = ELEMENT(settings.STAFF_CHARACTER_ELEMENT_TYPE)()
                character_key = GAME_SETTINGS.get("default_staff_character_key")
            else:
                new_char = ELEMENT(settings.PLAYER_CHARACTER_ELEMENT_TYPE)()
                character_key = GAME_SETTINGS.get("default_player_character_key")
            new_char.set_db_id(char_db_id)

            # do the connection
            new_char.set_account(self)
            new_char.setup_element(character_key)
        except Exception as e:
            traceback.print_exc()
            self.msg({"alert": _("That is not a valid character choice.")})
            return

        # Send puppet info to the client first.
        self.msg({
            "puppet": {
                "id": new_char.get_id(),
                "name": new_char.get_name(),
                "icon": getattr(new_char, "icon", None),
            }
        })

        # Set location
        try:
            location_key = CharacterLocation.load(char_db_id)
            location = Server.world.get_room(location_key)
            new_char.move_to(location)
        except KeyError:
            pass

        self.puppet_obj = new_char
        self.session.puid = char_db_id

        # add the character to the world
        Server.world.on_char_puppet(new_char)

        # final hook
        new_char.at_post_puppet()

    def unpuppet_object(self):
        """
        Disengage control over an object.

        Raises:
            RuntimeError With message about error.

        """
        obj = self.puppet_obj
        if obj:
            obj.at_pre_unpuppet()
            obj.set_session(None)

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

    def delete_character(self, char_db_id):
        """
        Delete an character.

        :param char_db_id:
        :return:
        """
        # use the playable_characters list to search
        characters = AccountCharacters.get_account_characters(self.id)
        if char_db_id not in characters:
            raise KeyError("Can not find the character.")

        self.unpuppet_object()

        # delete all character data.
        AccountCharacters.remove_character(self.id, char_db_id)
        CharacterInfo.remove_character(char_db_id)
        CharacterLocation.remove_character(char_db_id)
        CharacterInventory.remove_character(char_db_id)
        CharacterEquipments.remove_character(char_db_id)
        CharacterQuests.remove_character(char_db_id)
        CharacterSkills.remove_character(char_db_id)
        CharacterCombat.remove_character(char_db_id)
        HONOURS_MAPPER.remove_character(char_db_id)

    def at_cmdset_get(self):
        pass

    def check_password(self, username, password):
        """
        Check if the password is correct.
        """
        try:
            raw_password = Accounts.get_password(username)
        except KeyError:
            # Wrong username.
            return False

        return check_password(password, raw_password)

    def change_password(self, current_password, new_password):
        """
        Change the account's password.
        """
        if not self.check_password(self.username, current_password):
            self.msg({"alert":_("Incorrect password.")})
            return

        raw_password = make_password(new_password)
        Accounts.set_password(self.username, raw_password)

        self.msg({
            "alert":_("Password changed."),
            "pw_changed": True
        })

    def disconnect(self, reason):
        """
        Disconnect the session
        """
        if self.session:
            global _SESSIONS
            if not _SESSIONS:
                from evennia.server.sessionhandler import SESSIONS as _SESSIONS
            _SESSIONS.disconnect(self.session, reason)

            self.session = None
