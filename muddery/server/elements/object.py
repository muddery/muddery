"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

BaseObject is an object which can load it's data automatically.

"""

import ast, traceback
from django.core.exceptions import ObjectDoesNotExist
from evennia.objects.models import ObjectDB
from evennia.objects.objects import DefaultObject
from evennia.utils import logger
from evennia.utils.utils import make_iter, is_iter, lazy_property
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.events.event_trigger import EventTrigger
from muddery.server.utils import utils
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.utils.desc_handler import DESC_HANDLER
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.object_properties import ObjectProperties
from muddery.server.database.gamedata.object_keys import OBJECT_KEYS


class MudderyBaseObject(BaseElement, DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """
    element_type = "OBJECT"
    element_name = _("Object", "elements")
    model_name = "objects"

    # initialize all handlers in a lazy fashion
    @lazy_property
    def event(self):
        return EventTrigger(self)

    def get_id(self):
        """
        Get the object's id.

        :return: (number) object's id
        """
        return self.id

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        
        It will be called when swap its element_type, so it must keep
        old values.
        """
        super(MudderyBaseObject, self).at_object_creation()

        # set default values
        self.action = None
        self.condition = None
        self.icon = None

    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.

        All skills, contents will be removed too.
        """
        success = super(MudderyBaseObject, self).at_object_delete()
        if not success:
            return success

        OBJECT_KEYS.remove(self.id)
        self.states.clear()

        return True

    def at_init(self):
        """
        Load world data.
        """
        super(MudderyBaseObject, self).at_init()

        try:
            # Load db data.
            self.object_key = OBJECT_KEYS.get_key(self.id)
            self.load_data()
        except Exception as e:
            traceback.print_exc()
            logger.log_errmsg("%s(%s) can not load data:%s" % (self.get_object_key(), self.get_id(), e))
            
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

    def set_object_key(self, key, unique_type=None, level=None, reset_location=True):
        """
        Set data_info's model and key. It puts info into attributes.
            
        Args:
            key: (string) Key of the data info.
            level: (number) object's level.
            reset_location: (boolean) reset the object to its default location.
        """
        # Save data info's key and model
        OBJECT_KEYS.add(self.id, key, unique_type)
        self.object_key = key
        
        # Load data.
        try:
            # Load db data.
            self.load_data(level, reset_location=reset_location)
        except Exception as e:
            traceback.print_exc()
            logger.log_errmsg("%s(%s) can not load data:%s" % (key, self.get_id(), e))

        # call data_key hook
        self.after_object_key_changed()

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
            self.const_data_handler.add(field_name, getattr(record, field_name))

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
                self.const_data_handler.add(field_name, getattr(record, field_name))

    def load_data(self, level=None, reset_location=True):
        """
        Set data to the object.
        """
        if self.object_key:
            base_model = ELEMENT("OBJECT").model_name

            # Get the object's base data
            self.load_base_data(base_model, self.object_key)

            # reset element type
            if self.const.element_type:
                self.set_element_type(self.const.element_type)
            else:
                logger.log_errmsg("%s does not have element type." % self.const.element_type)

            # Load system data except base data.
            self.load_system_data(base_model, self.object_key)

            # Load custom properties.
            if level is None:
                level = self.states.load("level", None)
                if level is None:
                    # Use default level.
                    level = 0
                    if self.const_data_handler.has("level") and self.const.level:
                        level = self.const.level
                    self.states.save("level", level)

            self.load_custom_data(level)

        self.set_default_data()

        self.after_data_loaded()

        if not self.location and reset_location:
            self.set_location(self.const.location)

        # This object's class may be changed after load_data(), so do not add
        # codes here. You can add codes in after_data_loaded().

    def load_custom_data(self, level):
        """
        Load custom properties.
        """
        # Load values from db.
        values = {}
        for record in ObjectProperties.get_properties(self.get_object_key(), level):
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
                self.const_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
            else:
                # Set default mutable properties to prop.
                if not self.states.has(key):
                    self.states.save(key, self.get_custom_data_value(info["default"]))

    def get_custom_data_value(self, data):
        """
        Get a custom data's value
        :param value:
        :return:
        """
        if self.const_data_handler.has(data):
            # User another property'a value
            value = self.const_data_handler.get(data)
        else:
            try:
                value = ast.literal_eval(data)
            except (SyntaxError, ValueError) as e:
                # treat as a raw string
                value = data
        return value

    def after_object_key_changed(self):
        """
        Called at the object_key changed.
        """
        pass

    def set_default_data(self):
        """
        Set default data.
        """
        if not self.const_data_handler.has("name"):
            self.const_data_handler.add("name", "")

        if not self.const_data_handler.has("desc"):
            self.const_data_handler.add("desc", "")

        if not self.const_data_handler.has("condition"):
            self.const_data_handler.add("condition", None)

        if not self.const_data_handler.has("icon"):
            self.const_data_handler.add("icon", None)

        if not self.const_data_handler.has("location"):
            self.const_data_handler.add("location", None)

    def after_data_loaded(self):
        """
        Called after self.data_loaded().
        """        
        self.set_name(self.const.name)
        self.set_desc(self.const.desc)
        self.set_icon(self.const.icon)

    def reset_location(self):
        """
        Set object's location to its default location.

        Returns:
            None
        """
        self.set_location(self.const.location)

    def get_level(self):
        """
        Get the object's level.
        :return: (number) level
        """
        return self.states.load("level", 0)

    def set_level(self, level):
        """
        Set object's level.
        Args:
            level: object's new level

        Returns:
            None
        """
        self.states.save("level", level)
        self.load_custom_data(level)

    def set_element_type(self, element_type):
        """
        Set object's type.
        
        Args:
            element_key: (string) Element's key.
        """
        new_class = ELEMENT(element_type)
        if not new_class:
            logger.log_errmsg("Can not get %s's element type: %s." % (self.get_object_key(), element_type))
            return
        
        if type(self) == new_class:
            # No change.
            return

        # Set new class.
        self.__class__ = new_class
        if self.element_type != element_type:
            logger.log_errmsg("%s's element type %s is wrong!" % (self.get_object_key(), element_type))
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
            try:
                location_obj = utils.get_object_by_key(location)
            except ObjectDoesNotExist:
                logger.log_errmsg("%s can't find location %s!" % (self.get_object_key(), location))
                return
    
        if self.location == location_obj:
            # No change.
            return

        if self == location_obj:
            # Can't set location to itself.
            logger.log_errmsg("%s can't teleport itself to itself!" % self.get_object_key())
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

    def set_icon(self, icon_key):
        """
        Set object's icon.
        Args:
            icon_key: (String)icon's resource key.

        Returns:
            None
        """
        self.icon = icon_key

    def get_icon(self):
        """
        Get object's icon.
        :return:
        """
        return self.icon

    def get_object_key(self):
        """
        Get this object's element key.

        Args:
            default: (string) default value if can not find the data key.
        """
        return self.object_key

    def is_visible(self, caller):
        """
        If this object is visible to the caller.
        
        Return:
            boolean: visible
        """
        if not self.const.condition:
            return True

        return STATEMENT_HANDLER.match_condition(self.const.condition, caller, self)

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
        info = {"id": self.get_id(),
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
            desc_conditions = DESC_HANDLER.get(self.get_object_key())
            if desc_conditions:
                for item in desc_conditions:
                    if STATEMENT_HANDLER.match_condition(item["condition"], caller, self):
                        return item["desc"]
        return self.desc
        
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        return []

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
        if sessions:
            logger.log_info("Send message, %s: %s" % (self.id, text))

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

    def validate_property(self, key, value):
        """
        Check a property's value limit, return a validated value.

        Args:
            key: (string) values's key.
            value: (number) the value

        Return:
            (number) validated values.
        """
        # check limits
        max_value = None
        max_key = "max_" + key
        if self.states.has(max_key):
            max_value = self.states.load(max_key)
        elif self.const_data_handler.has(max_key):
            max_value = self.const_data_handler.get(max_key)

        if max_value is not None:
            if value > max_value:
                value = max_value

        min_value = 0
        min_key = "min_" + key
        if self.states.has(min_key):
            min_value = self.states.load(min_key)
        elif self.const_data_handler.has(min_key):
            min_value = self.const_data_handler.get(min_key)

        if value < min_value:
            value = min_value

        return value
