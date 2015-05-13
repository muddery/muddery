"""
Room

Rooms are simple containers that has no location of their own.

"""

from django.conf import settings
from muddery.typeclasses.objects import MudderyObject
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
    def at_object_receive(self, moved_obj, source_location):
        """
        Called after an object has been moved into this object.
        
        Args:
        moved_obj (Object): The object moved into this one
        source_location (Object): Where `moved_object` came from.
        
        """
        super(MudderyRoom, self).at_object_receive(moved_obj, source_location)
                
        # send surrounding changes to player
        change = {}
        if moved_obj.destination:
            change["exits"] = [{"dbref":moved_obj.dbref,
                                "name":moved_obj.name}]
        elif moved_obj.player:
            change["players"] = [{"dbref":moved_obj.dbref,
                                 "name":moved_obj.name}]
        elif moved_obj.is_typeclass(settings.BASE_CHARACTER_TYPECLASS):
            change["npcs"] = [{"dbref":moved_obj.dbref,
                              "name":moved_obj.name}]
        else:
            change["things"] = [{"dbref":moved_obj.dbref,
                                "name":moved_obj.name}]

        self.msg_contents({"obj_moved_in":change}, exclude=moved_obj)


    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        super(MudderyRoom, self).at_object_left(moved_obj, target_location)
                
        # send surrounding changes to player
        change = {}
        if moved_obj.destination:
            change["exits"] = [{"dbref":moved_obj.dbref,
                               "name":moved_obj.name}]
        elif moved_obj.player:
            change["players"] = [{"dbref":moved_obj.dbref,
                                 "name":moved_obj.name}]
        elif moved_obj.is_typeclass(settings.BASE_CHARACTER_TYPECLASS):
            change["npcs"] = [{"dbref":moved_obj.dbref,
                              "name":moved_obj.name}]
        else:
            change["things"] = [{"dbref":moved_obj.dbref,
                                "name":moved_obj.name}]

        self.msg_contents({"obj_moved_out":change}, exclude=moved_obj)
