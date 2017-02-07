"""
Room

Rooms are simple containers that has no location of their own.

"""

import ast
import traceback
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.objects import MudderyObject
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.game_settings import GAME_SETTINGS
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
    def at_init(self):
        """
        Load world data.
        """
        self.position = None
        super(MudderyRoom, self).at_init()


    def load_data(self):
        """
        Set data_info to the object.
        """
        super(MudderyRoom, self).load_data()

        self.position = None
        try:
            # set position
            position = getattr(self.dfield, "position", None)
            if position:
                self.position = ast.literal_eval(position)
        except Exception, e:
            logger.log_tracemsg("load position error: %s" % e)

        self.background = None
        try:
            # get background
            resource_key = getattr(self.dfield, "background", None)
            if resource_key:
                model_resource = apps.get_model(settings.WORLD_DATA_APP, settings.IMAGE_RESOURCES)
                if model_resource:
                    resource_info = model_resource.objects.get(key=resource_key)
                    self.background = resource_info.resource.url
        except Exception, e:
            logger.log_tracemsg("load background error: %s" % e)


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
        
        # add background
        info["background"] = self.background

        return info
        
    def get_exits(self):
        """
        Get this room's exits.
        """
        exits = {}
        for cont in self.contents:
            if cont.destination:
                exits[cont.get_data_key()] = (self.get_data_key(), cont.destination.get_data_key(),)
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
            condition = getattr(cont.dfield, "condition", None)
            if condition:
                if not STATEMENT_HANDLER.match_condition(condition, caller, self):
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
                elif type == "exits":
                    # get exits destination
                    if cont.destination:
                        dest = {"name": cont.destination.get_name(),
                                "position": cont.destination.position}
                        appearance["destination"] = dest
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
