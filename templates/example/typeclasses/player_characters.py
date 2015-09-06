"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.utils import logger
from muddery.typeclasses.player_characters import MudderyPlayerCharacter


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
    def return_status(self):
        """
        Get character's status.
        """
        status = super(PlayerCharacter, self).return_status()
        status["max_exp"] = self.max_exp
        status["max_hp"] = self.max_hp
        status["hp"] = self.db.hp
        status["max_mp"] = self.max_mp
        status["mp"] = self.db.mp
        status["attack"] = self.attack
        status["defence"] = self.defence

        return status


    def use_object(self, obj):
        """
        Use object.
        """
        if not obj:
            return

        result = ""

        # take effect
        try:
            result = self.take_effect(obj)
        except Exception, e:
            ostring = "Can not use %s: %s" % (obj.get_info_key(), e)
            logger.log_errmsg(ostring)

        # decrease object's number
        location = obj.location
        try:
            obj.decrease_num(1)
            if obj.db.number <= 0:
                obj.delete()
        except Exception, e:
            ostring = "An error occured when using %s: %s" % (obj.get_info_key(), e)
            logger.log_errmsg(ostring)

        if location:
            location.show_inventory()

        return result


    def take_effect(self, obj):
        """
        take item's effect
        """
        status_changed = False
        result = ""

        if hasattr(obj, "hp"):
            recover_hp = self.add_hp(obj.hp)
            if recover_hp > 0:
                status_changed = True
            result += "HP recovered by %s." % recover_hp

        if status_changed:
            self.show_status()

        return result


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


    def is_hp_full(self):
        """
        """
        return self.db.hp >= self.max_hp


    def recover_hp(self):
        """
        """
        self.db.hp = self.max_hp
        self.show_status()
        return


    def poison(self):
        """
        """
        self.db.hp /= 2
        self.show_status()
        return
