"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

import traceback
from django.conf import settings
from evennia.utils import logger
from evennia import DefaultAccount, DefaultGuest
from evennia.utils.utils import make_iter
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.character_location import CharacterLocation
from muddery.server.database.gamedata.character_inventory import CharacterInventory
from muddery.server.database.gamedata.character_equipments import CharacterEquipments
from muddery.server.database.gamedata.character_quests import CharacterQuests
from muddery.server.database.gamedata.character_skills import CharacterSkills
from muddery.server.database.gamedata.character_combat import CharacterCombat
from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.server import Server
from muddery.server.utils.localized_strings_handler import _


class MudderyAccount(DefaultAccount):
    """
    This class describes the actual OOC account (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_ACCOUNT_TYPECLASS.


    * available properties

     key (string) - name of account
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by account. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this account
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     swap_character(new_character, delete_old_character=False)
     execute_cmd(raw_string, session=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, account=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_account_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(session=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """
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
        # if we have saved protocol flags on ourselves, load them here.
        protocol_flags = self.attributes.get("_saved_protocol_flags", None)
        if session and protocol_flags:
            session.update_flags(**protocol_flags)

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

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        Evennia -> User
        This is the main route for sending data back to the user from the
        server.

        Args:
            text (str, optional): text data to send
            from_obj (Object or Account or list, optional): Object sending. If given, its
                at_msg_send() hook will be called. If iterable, call on all entities.
            session (Session or list, optional): Session object or a list of
                Sessions to receive this send. If given, overrules the
                default send behavior for the current
                MULTISESSION_MODE.
            options (list): Protocol-specific options. Passed on to the protocol.
        Kwargs:
            any (dict): All other keywords are passed on to the protocol.

        """
        if from_obj:
            # call hook
            for obj in make_iter(from_obj):
                try:
                    obj.at_msg_send(text=text, to_obj=self, **kwargs)
                except Exception:
                    # this may not be assigned.
                    logger.log_trace()
        try:
            if not self.at_msg_receive(text=text, **kwargs):
                # abort message to this account
                return
        except Exception:
            # this may not be assigned.
            pass

        kwargs["options"] = options

        # session relay
        logger.log_info("Send message, %s: %s" % (self, text))
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.data_out(text=text, **kwargs)

    def puppet_object(self, session, char_db_id):
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
        if not session:
            raise RuntimeError("Session not found")

        current_obj = self.get_puppet(session)
        if current_obj and current_obj.get_db_id() == char_db_id:
            # already puppeting this object
            self.msg("You are already puppeting this object.")
            return

        # do the puppeting
        if session.puppet:
            # cleanly unpuppet eventual previous object puppeted by this session
            self.unpuppet_object(session)
        # if we get to this point the character is ready to puppet or it
        # was left with a lingering account/session reference from an unclean
        # server kill or similar

        # Find the character to puppet.
        try:
            if self.is_staff:
                new_char = ELEMENT(settings.STAFF_CHARACTER_ELEMENT_TYPE)()
                character_key = GAME_SETTINGS.get("default_staff_character_key")
            else:
                new_char = ELEMENT(settings.PLAYER_CHARACTER_ELEMENT_TYPE)()
                character_key = GAME_SETTINGS.get("default_player_character_key")
            new_char.set_db_id(char_db_id)

            # do the connection
            new_char.set_account_id(self.id)
            new_char.set_session(session)
            new_char.setup_element(character_key)
        except:
            traceback.print_exc()
            session.msg({"alert": _("That is not a valid character choice.")})
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

        session.puid = char_db_id
        session.puppet = new_char

        # add the character to the world
        Server.world.on_char_puppet(new_char)

        # final hook
        new_char.at_post_puppet()

    def unpuppet_object(self, session):
        """
        Disengage control over an object.

        Args:
            session (Session or list): The session or a list of
                sessions to disengage from their puppets.

        Raises:
            RuntimeError With message about error.

        """
        for session in make_iter(session):
            obj = session.puppet
            if obj:
                obj.at_pre_unpuppet()
                obj.set_session(None)
                # obj.at_post_unpuppet(self, session=session)

                Server.world.on_char_unpuppet(obj)

            # Just to be sure we're always clear.
            session.puppet = None
            session.puid = None

    def delete_character(self, session, char_db_id):
        """
        Delete an character.

        :param char_db_id:
        :return:
        """
        # use the playable_characters list to search
        characters = AccountCharacters.get_account_characters(self.id)
        if char_db_id not in characters:
            raise KeyError("Can not find the character.")

        if session.puid == char_db_id:
            self.unpuppet_object(session)

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


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """
    pass