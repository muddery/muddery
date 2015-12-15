"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

import json
import ast
from django.conf import settings
from django.db.models.loading import get_model
from evennia.objects.objects import DefaultObject
from evennia.utils import logger
from evennia.utils.utils import make_iter
from evennia.utils.utils import lazy_property
from muddery.utils import utils
from muddery.utils.exception import MudderyError
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from muddery.utils.event_handler import EventHandler
from muddery.utils.localized_strings_handler import LS


class MudderyObject(DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """

    # these fields are reserved, can not used for other purpose.
    reserved_fields = set(["id",
                           "date_created",
                           "locks",
                           "tags",
                           "nattributes",
                           "dbref",
                           "is_typeclass",
                           "delete",
                           "swap_typeclass",
                           "db",
                           "ndb",
                           "objects",
                           "attr",
                           "save",
                           "delete",
                           ])

    # initialize all handlers in a lazy fashion
    @lazy_property
    def event(self):
        return EventHandler(self)


    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyObject, self).at_object_creation()
        
        # Call set_initial_data() when this object is first created.
        self.db.FIRST_CREATE = True


    def at_init(self):
        """
        Load world data.
        """
        super(MudderyObject, self).at_init()

        # need save before modify m2m fields
        self.save()

        try:
            # Load db data.
            self.load_data()
        except Exception, e:
            logger.log_tracemsg("%s can not load data:%s" % (self.dbref, e))


    def set_initial_data(self):
        """
        Initialize this object after data loaded.
        """
        pass


    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        # Send puppet info to the player and look around.
        self.msg("\n" + LS("You become {c%s{n.") % self.name + "\n")
        self.execute_cmd("look")

        if not settings.SOLO_MODE:
            # Notify other players in this location.
            if self.location:
                self.location.msg_contents("%s has entered the game." % self.name, exclude=[self])


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
                if not settings.SOLO_MODE:
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
    
    
    def set_data_info(self, key):
        """
        Set data_info's model and key. It puts info into attributes.
            
        Args:
            key: (string) Key of the data info.
        """
        # Save data info's key and model
        model = OBJECT_KEY_HANDLER.get_model(key)
        utils.set_obj_data_info(self, key, model)
        
        # Load data.
        self.load_data()

        # initialize with data
        if self.db.FIRST_CREATE:
            self.set_initial_data()
            del self.db.FIRST_CREATE


    def get_data_record(self):
        """
        Get object's data record from database.
        """
        # Get model and key names.
        key = self.get_info_key()
        if not key:
            return
        
        model = OBJECT_KEY_HANDLER.get_model(key)
        if not model:
            return
        
        # Get db model
        model_obj = get_model(settings.WORLD_DATA_APP, model)
        if not model_obj:
            raise MudderyError("%s can not open model %s" % (key, model))
        
        # Get data record.
        try:
            data = model_obj.objects.get(key=key)
        except Exception, e:
            raise MudderyError("%s can not find key %s" % (key, key))
        
        return data


    def load_data(self):
        """
        Set data_info to the object."
        """
        data = self.get_data_record()
        if not data:
            return

        if hasattr(data, "typeclass"):
            self.set_typeclass(data.typeclass)

        if hasattr(data, "name"):
            self.set_name(data.name)

        if hasattr(data, "alias"):
            self.set_alias(data.alias)

        if hasattr(data, "location"):
            self.set_location(data.location)

        if hasattr(data, "desc"):
            self.set_desc(data.desc)

        if hasattr(data, "lock"):
            self.set_lock(data.lock)

        if hasattr(data, "attributes"):
            self.set_attributes(data.attributes)

        if hasattr(data, "destination"):
            self.set_obj_destination(data.destination)
        
        # get other fields
        known_fields = set(["key",
                            "typeclass",
                            "name",
                            "alias",
                            "location",
                            "home",
                            "desc",
                            "lock",
                            "attributes",
                            "destination"])

        for field in data._meta.fields:
            if field.name in known_fields:
                # know fields have been already added.
                continue

            if field.name in self.reserved_fields:
                logger.log_errmsg("Can not set reserved field %s!" % field.name)
                continue

            # Set data.
            setattr(self, field.name, data.serializable_value(field.name))


    def set_typeclass(self, typeclass):
        """
        Set object's typeclass.
        
        Args:
        typeclass: (string) Typeclass's name.
        """
        if not typeclass:
            typeclass = settings.BASE_OBJECT_TYPECLASS
    
        if self.is_typeclass(typeclass, exact=True):
            # No change.
            return
    
        if not hasattr(self, 'swap_typeclass'):
            logger.log_errmsg("%s cannot have a type at all!" % self.get_info_key())
            return

        # Set new typeclass.
        self.swap_typeclass(typeclass, clean_attributes=False)
        if typeclass != self.typeclass_path:
            logger.log_errmsg("%s's typeclass %s is wrong!" % (self.get_info_key(), typeclass))
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


    def set_alias(self, aliases):
        """
        Set object's alias.
        
        Args:
        aliases: (string) Aliases of the object.
        """
        # merge the old and new aliases (if any)
        new_aliases = [alias.strip().lower() for alias in aliases.split(';')
                       if alias.strip()]

        set_new_aliases = set(new_aliases)
        set_current_aliases = set(self.aliases.all())
                   
        if set_new_aliases == set_current_aliases:
            # No change.
            return

        self.aliases.clear()
        self.aliases.add(new_aliases)
    
        # we need to trigger this here, since this will force
        # (default) Exits to rebuild their Exit commands with the new
        # aliases
        #self.at_cmdset_get(force_init=True)
    
        if self.destination:
            self.flush_from_cache()


    def set_location(self, location):
        """
        Set object's location.
        
        Args:
        location: (string) Location's name. Must be the key of data info.
        """
        location_obj = None
    
        if location:
            # If has location, search location object.
            location_obj = utils.search_obj_info_key(location)

            if not location_obj:
                logger.log_errmsg("%s can't find location %s!" % (self.get_info_key(), location))
                return
        
            location_obj = location_obj[0]
    
        if self.location == location_obj:
            # No change.
            return

        if self == location_obj:
            # Can't set location to itself.
            logger.log_errmsg("%s can't teleport itself to itself!" % self.get_info_key())
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
            home_obj = utils.search_obj_info_key(home)
        
            if not home_obj:
                logger.log_errmsg("%s can't find home %s!" % (self.get_info_key(), home))
                return
            
            home_obj = home_obj[0]
    
        if self.home == home_obj:
            # No change.
            return

        if self == home_obj:
            # Can't set home to itself.
            logger.log_errmsg("%s can't set home to itself!" % self.get_info_key())
            return
        
        self.home = home_obj


    def set_desc(self, desc):
        """
        Set object's description.
        
        Args:
        desc: (string) Description.
        """
        self.db.desc = desc


    def set_lock(self, lock):
        """
        Set object's lock.
        
        Args:
        lock: (string) Object's lock string.
        """
        if lock:
            try:
                self.locks.add(lock)
            except Exception:
                logger.log_errmsg("%s can't set lock %s." % (self.get_info_key(), lock))


    def set_attributes(self, attributes):
        """
        Set object's attribute.
        
        Args:
        attributes: (string) Attribues in form of python dict. Such as: "{'age':'22', 'career':'warrior'}"
        """
        if not attributes:
            return
        
        # Set attributes.
        attr = {}
        try:
            # Convert string to dict
            attributes = ast.literal_eval(attributes)
        except Exception, e:
            logger.log_errmsg("%s can't load attributes %s: %s" % (self.get_info_key(), attributes, e))
    
        for key in attr:
            # Add attributes.
            try:
                self.attributes.add(key, attr[key])
            except Exception:
                logger.log_errmsg("%s can't set attribute %s!" % (self.get_info_key(), key))


    def set_obj_destination(self, destination):
        """
        Set object's destination
        
        Args:
        destination: (string) Destination's name. Must be the key of data info.
        """
        destination_obj = None
    
        if destination:
            # If has destination, search destination object.
            destination_obj = utils.search_obj_info_key(destination)
        
        if not destination_obj:
            logger.log_errmsg("%s can't find destination %s!" % (self.get_info_key(), destination))
            return
        
        destination_obj = destination_obj[0]
    
        if self.destination == destination_obj:
            # No change.
            return

        if self == destination_obj:
            # Can't set destination to itself.
            logger.log_errmsg("%s can't set destination to itself!" % self.get_info_key())
            return
    
        self.destination = destination_obj


    def set_detail(self, key, detail):
        """
        Set object's detail.
        
        Args:
        key: (string) Detail's key.
        detail: (string) Detail's info.
        """
        pass


    def get_info_key(self):
        """
        Get data info's key.
        """
        key = self.attributes.get(key="key", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)
        if not key:
            key = ""
        return key


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
                "cmds": self.get_available_commands(caller)}
                
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
