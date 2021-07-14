"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

BaseObject is an object which can load it's data automatically.

"""

import ast, traceback
from django.conf import settings
from evennia.objects.models import ObjectDB
from evennia.objects.objects import DefaultObject
from evennia.utils import logger
from evennia.utils.utils import make_iter, is_iter, lazy_property
from evennia.typeclasses.models import DbHolder
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.events.event_trigger import EventTrigger
from muddery.server.utils.data_field_handler import DataFieldHandler
from muddery.server.utils.properties_handler import PropertiesHandler
from muddery.server.utils import utils
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.utils.desc_handler import DESC_HANDLER
from muddery.server.typeclasses.base_typeclass import BaseTypeclass
from muddery.server.mappings.typeclass_set import TYPECLASS
from muddery.server.dao.worlddata import WorldData
from muddery.server.dao.object_properties import ObjectProperties


class MudderyBaseObject(BaseTypeclass, DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """
    typeclass_key = "OBJECT"
    typeclass_name = _("Object", "typeclasses")
    model_name = "objects"

    # initialize all handlers in a lazy fashion
    @lazy_property
    def event(self):
        return EventTrigger(self)

    @lazy_property
    def system_data_handler(self):
        return DataFieldHandler(self)

    # @property system stores object's system data.
    def __system_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._system_holder
        except AttributeError:
            self._system_holder = DbHolder(self, "system_data", manager_name='system_data_handler')
            return self._system_holder

    # @system.setter
    def __system_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use self.system.name=value instead."
        raise Exception(string)

    # @system.deleter
    def __system_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the system data object!")
    system = property(__system_get, __system_set, __system_del)

    @lazy_property
    def custom_properties_handler(self):
        return PropertiesHandler(self)

    # @property custom stores object's custom data.
    def __prop_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._custom_holder
        except AttributeError:
            self._custom_holder = DbHolder(self, "custom_properties", manager_name='custom_properties_handler')
            return self._custom_holder

    # @prop.setter
    def __prop_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use self.prop.name=value instead."
        raise Exception(string)

    # @prop.deleter
    def __prop_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the custom properties object!")
    prop = property(__prop_get, __prop_set, __prop_del)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        
        It will be called when swap its typeclass, so it must keep
        old values.
        """
        super(MudderyBaseObject, self).at_object_creation()

        # set default values
        self.action = None
        self.condition = None
        self.icon = None
        self.desc = ""

    def at_init(self):
        """
        Load world data.
        """
        super(MudderyBaseObject, self).at_init()

        self.condition = None
        self.action = None
        self.icon = None
        self.desc = ""
        
        try:
            # Load db data.
            self.load_data()
        except Exception as e:
            traceback.print_exc()
            logger.log_errmsg("%s(%s) can not load data:%s" % (self.get_data_key(), self.dbref, e))
            
        # This object's class may be changed after load_data(), so do not add
        # codes here. You can add codes in after_data_loaded() which is called
        # after load_data().

    def after_creation(self):
        """
        Called once, after the object is created by Muddery.
        """
        pass
    
    def at_post_unpuppet(self, player, session=None, **kwargs):
        """
        We stove away the character when the player goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the player logged off ("headless", so to say).

        Args:
            player (Player): The player object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
        """
        if not self.sessions.count():
            # only remove this char from grid if no sessions control it anymore.
            if self.location: # have to check, in case of multiple connections closing
                if not GAME_SETTINGS.get("solo_mode"):
                    # Notify other players in this location.
                    self.location.msg_contents("%s has left the game." % self.name, exclude=[self])

                # Save last location.
                self.db.prelogout_location = self.location
                self.location = None

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """
        Called after an object has been moved into this object.

        Args:
            moved_obj (Object): The object moved into this one
            source_location (Object): Where `moved_object` came from.

        """
        # Call hook on source location
        if source_location:
            if source_location != self:
                source_location.at_object_left(moved_obj, moved_obj.location)

    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        pass

    def set_data_key(self, key, level=None, reset_location=True):
        """
        Set data_info's model and key. It puts info into attributes.
            
        Args:
            key: (string) Key of the data info.
            level: (number) object's level.
            reset_location: (boolean) reset the object to its default location.
        """
        # Save data info's key and model
        utils.set_obj_data_key(self, key)
        
        # Load data.
        try:
            # Load db data.
            self.load_data(level, reset_location=reset_location)
        except Exception as e:
            traceback.print_exc()
            logger.log_errmsg("%s(%s) can not load data:%s" % (key, self.dbref, e))

        # call data_key hook
        self.after_data_key_changed()

    def load_base_data(self, base_model, key):
        """
        Get object's system data from database.

        Args:
            base_model: (String) base data's table name.
            key: (String) object's data key.

        Returns:
            None
        """
        # Get data record.
        try:
            fields = WorldData.get_fields(base_model)
            record = WorldData.get_table_data(base_model, key=key)
            record = record[0]
        except Exception as e:
            logger.log_errmsg("Can not find key %s in %s" % (key, base_model))
            return

        # Set data.
        for field_name in fields:
            setattr(self.system, field_name, getattr(record, field_name))

    def load_system_data(self, base_model, key):
        """
        Get object's system data from database except base data.

        Args:
            base_model: (String) base data's table name.
            key: (String) object's data key.

        Returns:
            None
        """
        # Get models.
        for data_model in self.get_models():
            if data_model == base_model:
                continue

            # Get data record.
            try:
                fields = WorldData.get_fields(data_model)
                record = WorldData.get_table_data(data_model, key=key)
                record = record[0]
            except Exception as e:
                logger.log_errmsg("Can not find key %s in %s" % (key, data_model))
                continue

            # Set data.
            for field_name in fields:
                setattr(self.system, field_name, getattr(record, field_name))

    def load_data(self, level=None, reset_location=True):
        """
        Set data to the object.
        """
        key = self.get_data_key()
        if key:
            base_model = TYPECLASS("OBJECT").model_name

            # Get the object's base data
            self.load_base_data(base_model, key)

            # reset typeclass
            typeclass = getattr(self.system, "typeclass", "")
            if typeclass:
                self.set_typeclass(typeclass)
            else:
                logger.log_errmsg("%s does not have a typeclass." % key)

            # Load system data except base data.
            self.load_system_data(base_model, key)

            # Load custom properties.
            if level is None:
                if self.attributes.has("level"):
                    level = self.db.level
                else:
                    # Use default level.
                    level = getattr(self.system, "level", 0)
                    self.db.level = level

            self.load_custom_properties(level)

        self.after_data_loaded()

        if not self.location and reset_location:
            self.set_location(getattr(self.system, "location", ""))

        # This object's class may be changed after load_data(), so do not add
        # codes here. You can add codes in after_data_loaded().

    def load_custom_properties(self, level):
        """
        Load custom properties.
        """
        # Get object level.
        if level is None:
            level = self.db.level

        # Load values from db.
        values = {}
        for record in ObjectProperties.get_properties(self.get_data_key(), level):
            key = record.property
            serializable_value = record.value
            if serializable_value == "":
                value = None
            else:
                try:
                    value = ast.literal_eval(serializable_value)
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = serializable_value
            values[key] = value

        # Set values.
        for key, info in self.get_properties_info().items():
            if not info["mutable"]:
                self.custom_properties_handler.add(key, values.get(key, ast.literal_eval(info["default"])))

        # Set default mutable custom properties.
        self.set_mutable_custom_properties()

    def set_mutable_custom_properties(self):
        """
        Set default mutable custom properties.
        """
        for key, info in self.get_properties_info().items():
            if info["mutable"]:
                # Set default mutable properties to prop.
                if not self.custom_properties_handler.has(key):
                    default = info["default"]
                    if self.custom_properties_handler.has(default):
                        # User another property'a value
                        value = self.custom_properties_handler.get(default)
                    else:
                        try:
                            value = ast.literal_eval(default)
                        except (SyntaxError, ValueError) as e:
                            # treat as a raw string
                            value = default
                    self.custom_properties_handler.add(key, value)

    def after_data_key_changed(self):
        """
        Called at data_key changed.
        """
        pass

    def after_data_loaded(self):
        """
        Called after self.data_loaded().
        """        
        self.set_name(getattr(self.system, "name", ""))

        self.set_desc(getattr(self.system, "desc", ""))

        self.condition = getattr(self.system, "condition", "")
        
        self.action = getattr(self.system, "action", "")

        # set icon
        self.set_icon(getattr(self.system, "icon", ""))

    def reset_location(self):
        """
        Set object's location to its default location.

        Returns:
            None
        """
        if hasattr(self.system, "location"):
            self.set_location(self.system.location)

    def set_level(self, level):
        """
        Set object's level.
        Args:
            level: object's new level

        Returns:
            None
        """
        if self.db.level == level:
            return

        self.db.level = level
        self.load_custom_properties(level)

    def set_typeclass(self, typeclass_key):
        """
        Set object's typeclass.
        
        Args:
            typeclass_key: (string) Typeclass's key.
        """
        typeclass_cls = TYPECLASS(typeclass_key)
        if not typeclass_cls:
            logger.log_errmsg("Can not get %s's typeclass: %s." % (self.get_data_key(), typeclass_key))
            return
        
        if type(self) == typeclass_cls:
            # No change.
            return

        if not hasattr(self, 'swap_typeclass'):
            logger.log_errmsg("%s cannot have a type at all!" % self.get_data_key())
            return

        # Set new typeclass.
        # It will call target typeclass's at_object_creation hook.
        # You should prevent at_object_creation rewrite current attributes.
        self.swap_typeclass(typeclass_cls, clean_attributes=False)
        if typeclass_cls.path != self.typeclass_path:
            logger.log_errmsg("%s's typeclass %s is wrong!" % (self.get_data_key(), typeclass_cls.path))
            return

    def set_name(self, name):
        """
        Set object's name.
        
        Args:
        name: (string) Name of the object.
        """
        if name == self.name:
            # No change.
            return
    
        self.name = name

        # we need to trigger this here, since this will force
        # (default) Exits to rebuild their Exit commands with the new
        # aliases
        #self.at_cmdset_get(force_init=True)

        if self.destination:
            self.flush_from_cache()

    def get_name(self):
        """
        Get player character's name.
        """
        return self.name

    def set_location(self, location):
        """
        Set object's location.
        
        Args:
        location: (string) Location's name. Must be the key of data info.
        """
        location_obj = None
    
        if location:
            # If has location, search location object.
            location_obj = utils.search_obj_data_key(location)

            if not location_obj:
                logger.log_errmsg("%s can't find location %s!" % (self.get_data_key(), location))
                return
        
            location_obj = location_obj[0]
    
        if self.location == location_obj:
            # No change.
            return

        if self == location_obj:
            # Can't set location to itself.
            logger.log_errmsg("%s can't teleport itself to itself!" % self.get_data_key())
            return
    
        # try the teleport
        self.move_to(location_obj, quiet=True, to_none=True)

    def set_desc(self, desc):
        """
        Set object's description.
        
        Args:
        desc: (string) Description.
        """
        self.desc = desc

    def set_obj_destination(self, destination):
        """
        Set object's destination
        
        Args:
        destination: (string) Destination's name. Must be the key of data info.
        """
        if not destination:
            # remove destination
            self.destination = destination
            return

        # set new destination
        destination_obj = None
    
        if destination:
            # If has destination, search destination object.
            destination_obj = utils.search_obj_data_key(destination)
        
        if not destination_obj:
            logger.log_errmsg("%s can't find destination %s!" % (self.get_data_key(), destination))
            return
        
        destination_obj = destination_obj[0]
    
        if self.destination == destination_obj:
            # No change.
            return

        if self == destination_obj:
            # Can't set destination to itself.
            logger.log_errmsg("%s can't set destination to itself!" % self.get_data_key())
            return
    
        self.destination = destination_obj

    def set_icon(self, icon_key):
        """
        Set object's icon.
        Args:
            icon_key: (String)icon's resource key.

        Returns:
            None
        """
        self.icon = getattr(self.system, "icon", None)

    def get_data_key(self, default=""):
        """
        Get data's key.

        Args:
            default: (string) default value if can not find the data key.
        """
        key = self.attributes.get(key="key", category=settings.DATA_KEY_CATEGORY, strattr=True)
        if not key:
            key = default
        return key

    def is_visible(self, caller):
        """
        If this object is visible to the caller.
        
        Return:
            boolean: visible
        """
        if not self.condition:
            return True

        return STATEMENT_HANDLER.match_condition(self.condition, caller, self)

    def get_surroundings(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        pass

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # Get name, description and available commands.
        info = {"dbref": self.dbref,
                "name": self.get_name(),
                "desc": self.get_desc(caller),
                "cmds": self.get_available_commands(caller),
                "icon": getattr(self, "icon", None)}
        return info

    def get_desc(self, caller):
        """
        This returns object's descriptions on different conditions.
        """
        if caller:
            desc_conditions = DESC_HANDLER.get(self.get_data_key())
            if desc_conditions:
                for item in desc_conditions:
                    if STATEMENT_HANDLER.match_condition(item["condition"], caller, self):
                        return item["desc"]
        return self.desc
        
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.action:
            commands = [{"name":self.action, "cmd":"action", "args":self.dbref}]
        return commands

    @classmethod
    def get_event_trigger_types(cls):
        """
        Get an object's available event triggers.
        """
        return []

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        Emits something to a session attached to the object.

        Args:
            text (str, optional): The message to send
            from_obj (obj, optional): object that is sending. If
                given, at_msg_send will be called
            session (Session or list, optional): Session or list of
                Sessions to relay data to, if any. If set, will
                force send to these sessions. If unset, who receives the
                message depends on the MULTISESSION_MODE.

        Notes:
            `at_msg_receive` will be called on this Object.
            All extra kwargs will be passed on to the protocol.

        """
        # Send messages to the client. Messages are in format of JSON.
        # try send hooks
        if from_obj:
            try:
                from_obj.at_msg_send(text=text, to_obj=self, **kwargs)
            except Exception:
                logger.log_trace()
        try:
            if not self.at_msg_receive(text=text, **kwargs):
                # if at_msg_receive returns false, we abort message to this object
                return
        except Exception:
            logger.log_trace()

        kwargs["options"] = options
                                                        
        # relay to session(s)
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.msg(text=text, **kwargs)

    def msg_contents(self, text=None, exclude=None, from_obj=None, mapping=None, **kwargs):
        """
        Emits a message to all objects inside this object.

        Send text in JSON format.
        """
        contents = self.contents
        if exclude:
            exclude = make_iter(exclude)
            contents = [obj for obj in contents if obj not in exclude]

        for obj in contents:
            obj.msg(text=text, from_obj=from_obj, **kwargs)

    def got_message(self, caller, message):
        """
        Receive a message from an object.

        :param caller: talker.
        :param message: content.
        """
        pass

    def search_dbref(self, dbref, location=None):
        """
        Search as an object by its dbref.

        Args:
            dbref: (string)dbref.

        Returns:
            The object or None.
        """
        match = ObjectDB.objects.dbref_search(dbref)

        if match and location:
            # match the location
            if is_iter(location):
                if not [l for l in location if match.location == l]:
                    match = None
            elif match.location != location:
                match = None

        return match

    def announce_move_from(self, destination, msg=None, mapping=None, **kwargs):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        Args:
            destination (Object): The place we are going to.
            msg (str, optional): a replacement message.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.

        """
        if not self.location:
            return
        if msg:
            string = msg
        else:
            string = _("{object} is leaving {origin}, heading for {destination}.")

        location = self.location
        exits = [o for o in location.contents if o.location is location and o.destination is destination]
        if not mapping:
            mapping = {}

        mapping.update({
            "object": self.get_name(),
            "exit": exits[0].get_name() if exits else "",
            "origin": location.get_name() if location else "",
            "destination": destination.get_name() if destination else "",
        })

        location.msg_contents(string.format(**mapping), exclude=(self, ))

    def announce_move_to(self, source_location, msg=None, mapping=None, **kwargs):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.

        Args:
            source_location (Object): The place we came from
            msg (str, optional): the replacement message if location.
            mapping (dict, optional): additional mapping objects.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            You can override this method and call its parent with a
            message to simply change the default message.  In the string,
            you can use the following as mappings (between braces):
                object: the object which is moving.
                exit: the exit from which the object is moving (if found).
                origin: the location of the object before the move.
                destination: the location of the object after moving.

        """

        if not source_location and self.location.has_account:
            # This was created from nowhere and added to an account's
            # inventory; it's probably the result of a create command.
            string = "You now have %s in your possession." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        if source_location:
            if msg:
                string = msg
            else:
                string = _("{object} arrives to {destination} from {origin}.")
        else:
            string = _("{object} arrives to {destination}.")

        origin = source_location
        destination = self.location
        exits = []
        if origin:
            exits = [o for o in destination.contents if o.location is destination and o.destination is origin]

        if not mapping:
            mapping = {}

        mapping.update({
            "object": self.get_name(),
            "exit": exits[0].get_name() if exits else "",
            "origin": origin.get_name() if origin else "",
            "destination": destination.get_name() if destination else "",
        })

        destination.msg_contents(string.format(**mapping), exclude=(self, ))

