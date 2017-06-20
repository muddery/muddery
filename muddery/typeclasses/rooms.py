"""
Room

Rooms are simple containers that has no location of their own.

"""

import ast
import traceback
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS
from evennia.utils import logger
from evennia.objects.objects import DefaultRoom


class MudderyRoom(MudderyObject, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        """
        super(MudderyRoom, self).at_object_creation()

        self.peaceful = False
        self.position = None
        self.background = None

    def after_data_loaded(self):
        """
        Set data_info to the object.
        """
        super(MudderyRoom, self).after_data_loaded()
        
        self.peaceful = getattr(self.dfield, "peaceful", False)

        self.position = None
        try:
            # set position
            position = getattr(self.dfield, "position", None)
            if position:
                self.position = ast.literal_eval(position)
        except Exception, e:
            logger.log_tracemsg("load position error: %s" % e)

        # get background
        self.background = None
        resource_key = getattr(self.dfield, "background", None)
        if resource_key:
            try:
                resource_info = DATA_SETS.image_resources.objects.get(key=resource_key)
                self.background = resource_info.resource.name
            except Exception, e:
                logger.log_tracemsg("Load background %s error: %s" % (resource_key, e))

    def at_object_receive(self, moved_obj, source_location):
        """
        Called after an object has been moved into this object.
        
        Args:
        moved_obj (Object): The object moved into this one
        source_location (Object): Where `moved_object` came from.
        
        """
        super(MudderyRoom, self).at_object_receive(moved_obj, source_location)

        if not GAME_SETTINGS.get("solo_mode"):
            # send surrounding changes to player
            type = self.get_surrounding_type(moved_obj)
            if type:
                change = {type: [{"dbref": moved_obj.dbref,
                                  "name": moved_obj.get_name()}]}
                self.msg_contents({"obj_moved_in": change}, exclude=moved_obj)

        # trigger event
        if moved_obj.has_player:
            self.event.at_character_move_in(moved_obj)

    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        super(MudderyRoom, self).at_object_left(moved_obj, target_location)

        if not GAME_SETTINGS.get("solo_mode"):
            # send surrounding changes to player
            type = self.get_surrounding_type(moved_obj)
            if type:
                change = {type: [{"dbref": moved_obj.dbref,
                                  "name": moved_obj.get_name()}]}
                self.msg_contents({"obj_moved_out": change}, exclude=moved_obj)

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(MudderyRoom, self).get_appearance(caller)
        
        # peaceful
        info["peaceful"] = getattr(self, "peaceful", False)

        # add background
        info["background"] = getattr(self, "background", None)

        return info
        
    def get_exits(self):
        """
        Get this room's exits.
        """
        exits = {}
        for cont in self.contents:
            if cont.destination:
                exits[cont.get_data_key()] = {"from": self.get_data_key(),
                                              "to": cont.destination.get_data_key()}
        return exits

    def get_surroundings(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description, commands and all objects in it
        info = {"exits": [],
                "npcs": [],
                "things": [],
                "players": [],
                "offlines": []}

        visible = (cont for cont in self.contents if cont != caller and
                   cont.access(caller, "view"))

        if GAME_SETTINGS.get("solo_mode"):
            visible = (cont for cont in visible if not cont.has_player)

        for cont in visible:
            # only show objects that match the condition
            if not cont.is_visible(caller):
                continue

            type = self.get_surrounding_type(cont)
            if type:
                appearance = {}

                if type == "npcs":
                    # add quest status
                    if hasattr(cont, "have_quest"):
                        provide_quest, complete_quest = cont.have_quest(caller)
                        appearance["provide_quest"] = provide_quest
                        appearance["complete_quest"] = complete_quest
                elif type == "offlines":
                    continue

                appearance["dbref"] = cont.dbref
                appearance["name"] = cont.get_name()
                appearance["key"] = cont.get_data_key()
                
                info[type].append(appearance)

        return info

    def get_surrounding_type(self, obj):
        """
        Get surrounding's view type.
        """
        if obj.destination:
            return "exits"
        elif obj.is_typeclass(settings.BASE_GENERAL_CHARACTER_TYPECLASS, exact=False):
            if obj.is_typeclass(settings.BASE_CHARACTER_TYPECLASS, exact=False):
                if obj.has_player:
                    return "players"
                else:
                    return "offlines"
            else:
                return "npcs"
        else:
            return "things"
