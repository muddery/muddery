"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import random
from django.conf import settings
from django.apps import apps
from evennia.utils import logger
from muddery.typeclasses.player_characters import MudderyPlayerCharacter
from muddery.utils.localized_strings_handler import LS
import traceback


class PlayerCharacter(MudderyPlayerCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        super(PlayerCharacter, self).at_object_creation()

        try:
            model_career = apps.get_model(settings.WORLD_DATA_APP, settings.CHARACTER_CAREERS)
            if model_career:
                careers = model_career.objects.all()
                if careers:
                    career = random.choice(careers)
                    self.db.career = career.key
        except Exception, e:
            pass


    def add_hp(self, hp):
        """
        Add character's hp.
        """
        recover_hp = int(hp)
                
        if self.db.hp < 0:
            self.db.hp = 0

        if self.db.hp + recover_hp > self.max_hp:
            recover_hp = self.max_hp - self.db.hp

        if recover_hp > 0:
            self.db.hp += recover_hp

        return recover_hp
