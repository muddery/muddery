"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from __future__ import print_function

import json
import ast
from django.conf import settings
from django.apps import apps
from evennia.objects.objects import DefaultObject
from evennia.utils import logger
from evennia.utils.utils import make_iter
from evennia.utils.utils import lazy_property
from evennia.typeclasses.models import DbHolder
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.data_field_handler import DataFieldHandler
from muddery.utils import utils
from muddery.utils.exception import MudderyError
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from muddery.utils.event_handler import EventHandler
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS


class MudderyObject(DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """
    # initialize all handlers in a lazy fashion
    @lazy_property
    def event(self):
        return EventHandler(self)

    @lazy_property
    def datafields(self):
        return DataFieldHandler(self)

    #@property dfield
    def __dfield_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._dfield_holder
        except AttributeError:
            self._dfield_holder = DbHolder(self, "datafield", manager_name='datafields')
            return self._dfield_holder

    #@dfield.setter
    def __dfield_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use dfield.attr=value instead."
        raise Exception(string)

    #@dfield.deleter
    def __dfield_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the dfield object!")
    dfield = property(__dfield_get, __dfield_set, __dfield_del)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        
        It will be called when swap its typeclass, so it must keep
        old values.
        """
        super(MudderyObject, self).at_object_creation()

        self.typeclass_key = None
        self.condition = None
        self.icon = None

    def at_init(self):
        """
        Load world data.
        """
        super(MudderyObject, self).at_init()

        self.typeclass_key = None
        self.condition = None
        self.icon = None
        
        try:
            # Load db data.
            self.load_data()
        except Exception, e:
            logger.log_tracemsg("%s can not load data:%s" % (self.dbref, e))
            
        # This object's class may be changed after load_data(), so do not add
        # codes here. You can add codes in after_data_loaded() which is called
        # after load_data().
    
    def at_post_unpuppet(self, player, session=None):
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

    def at_object_receive(self, moved_obj, source_location):
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

    def set_data_key(self, key, set_location=True):
        """
        Set data_info's model and key. It puts info into attributes.
            
        Args:
            key: (string) Key of the data info.
        """
        current_key = self.get_data_key(default=None)
        if current_key is not None:
            # Has data key
            if key == current_key:
                # Key has not changed.
                return
        
        # Save data info's key and model
        utils.set_obj_data_key(self, key)
        
        # Load data.
        self.load_data(set_location=set_location)

        # call data_key hook
        self.after_data_key_changed()

    def load_data_fields(self, key):
        """
        Get object's data record from database.

        Args:
            key: (String) object's data key.

        Returns:
            None
        """
        # Get model and key names.
        if not key:
            key = self.get_data_key()
            if not key:
                return

        if key[:len(settings.REVERSE_EXIT_PREFIX)] == settings.REVERSE_EXIT_PREFIX:
            # Reverse exit loads data without key's prefix.
            key = key[len(settings.REVERSE_EXIT_PREFIX):]

        data_models = OBJECT_KEY_HANDLER.get_models(key)

        for data_model in data_models:
            # Get db model
            model_obj = apps.get_model(settings.WORLD_DATA_APP, data_model)
            if not model_obj:
                logger.log_errmsg("%s can not open model %s" % (key, data_model))
                continue

            # Get data record.
            try:
                data = model_obj.objects.get(key=key)
            except Exception, e:
                logger.log_errmsg("%s can not find key %s" % (key, key))
                continue

            # Set data.
            for field in data._meta.fields:
                setattr(self.dfield, field.name, data.serializable_value(field.name))

    def load_data(self, set_location=True):
        """
        Set data to the object."
        """
        key = self.get_data_key()
        if key:
            self.load_data_fields(key)

            # reset typeclass
            if key[:len(settings.REVERSE_EXIT_PREFIX)] == settings.REVERSE_EXIT_PREFIX:
                # Reverse exit's typeclass can only be set to settings.REVERSE_EXIT_TYPECLASS_PATH.
                typeclass = settings.REVERSE_EXIT_TYPECLASS_PATH
            else:
                typeclass = getattr(self.dfield, "typeclass", "")
            self.set_typeclass(typeclass)

        self.after_data_loaded()

        if not self.location and set_location:
            self.set_location(getattr(self.dfield, "location", ""))

        # This object's class may be changed after load_data(), so do not add
        # codes here. You can add codes in after_data_loaded().

    def after_data_key_changed(self):
        """
        Called at data_key changed.
        """
        pass

    def after_data_loaded(self):
        """
        Called after self.data_loaded().
        """        
        self.set_name(getattr(self.dfield, "name", ""))

        self.set_desc(getattr(self.dfield, "desc", ""))

        self.condition = getattr(self.dfield, "condition", "")

        # set icon
        self.set_icon(getattr(self.dfield, "icon", ""))

    def reset_location(self):
        """
        Set object's location to its default location.

        Returns:
            None
        """
        if hasattr(self.dfield, "location"):
            self.set_location(self.dfield.location)

    def set_typeclass(self, typeclass_key):
        """
        Set object's typeclass.
        
        Args:
            typeclass_key: (string) Typeclass's key.
        """
        typeclass_path = ""
        try:
            data = DATA_SETS.typeclasses.objects.get(key=typeclass_key)
            typeclass_path = data.path
        except Exception, e:
            pass

        if not typeclass_path:
            if typeclass_key:
                typeclass_path = typeclass_key
            else:
                typeclass_path = settings.BASE_OBJECT_TYPECLASS
        
        if self.is_typeclass(typeclass_path, exact=True):
            # No change.
            return

        if not hasattr(self, 'swap_typeclass'):
            logger.log_errmsg("%s cannot have a type at all!" % self.get_data_key())
            return

        # Set new typeclass.
        # It will call target typeclass's at_object_creation hook.
        # You should prevent at_object_creation rewrite current attributes.
        self.swap_typeclass(typeclass_path, clean_attributes=False)
        if typeclass_path != self.typeclass_path:
            logger.log_errmsg("%s's typeclass %s is wrong!" % (self.get_data_key(), typeclass_path))
            return
        
        self.typeclass_key = typeclass_key

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

    def set_home(self, home):
        """
        Set object's home.
        
        Args:
        home: (string) Home's name. Must be the key of data info.
        """
        home_obj = None
    
        if home:
            # If has home, search home object.
            home_obj = utils.search_obj_data_key(home)
        
            if not home_obj:
                logger.log_errmsg("%s can't find home %s!" % (self.get_data_key(), home))
                return
            
            home_obj = home_obj[0]
    
        if self.home == home_obj:
            # No change.
            return

        if self == home_obj:
            # Can't set home to itself.
            logger.log_errmsg("%s can't set home to itself!" % self.get_data_key())
            return
        
        self.home = home_obj

    def set_desc(self, desc):
        """
        Set object's description.
        
        Args:
        desc: (string) Description.
        """
        self.db.desc = desc

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
        self.icon = None
        icon_key = getattr(self.dfield, "icon", None)
        if icon_key:
            try:
                resource_info = DATA_SETS.icon_resources.objects.get(key=icon_key)
                self.icon = resource_info.resource.name
            except Exception, e:
                logger.log_errmsg("Load icon %s error: %s" % (icon_key, e))

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
                "name": self.name,
                "desc": self.db.desc,
                "cmds": self.get_available_commands(caller),
                "icon": getattr(self, "icon", None)}

        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        return commands

    def msg(self, text=None, from_obj=None, session=None, **kwargs):
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
        """
        raw = kwargs.get("raw", False)
        if not raw:
            try:
                text = json.dumps(text)
            except Exception, e:
                text = json.dumps({"err": "There is an error occurred while outputing messages."})
                logger.log_errmsg("json.dumps failed: %s" % e)
        else:
            text = to_str(text, force_string=True) if text != None else ""

        # set raw=True
        if kwargs:
            kwargs["raw"] = True
        else:
            kwargs = {"raw": True}
        """

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
                                                        
        # relay to session(s)
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.msg(text=text, **kwargs)
