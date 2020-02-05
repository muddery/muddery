"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

import traceback
from evennia.utils import logger
from muddery.typeclasses.character import MudderyCharacter


class Character(MudderyCharacter):
    """
    Custom character class.

    """
    typeclass_key = "CHARACTER"

    def set_default_custom_properties(self):
        """
        Set default mutable custom properties.
        """
        if not self.custom_properties_handler.has("exp"):
            self.prop.exp = 0

        if not self.custom_properties_handler.has("hp"):
            self.prop.hp = self.prop.max_hp
            if self.prop.hp is None:
                logger.log_err("%s's hp is empty." % self.get_data_key())

        if not self.custom_properties_handler.has("mp"):
            self.prop.mp = self.prop.max_mp
            if self.prop.mp is None:
                logger.log_err("%s's mp is empty." % self.get_data_key())

    def reborn(self):
        """
        Reborn after being killed.
        """
        super(Character, self).reborn()
        
        # Recover hp and mp.
        values = {
            "hp": self.prop.max_hp,
            "mp": self.prop.max_mp
        }
        self.set_properties(values)
        
    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        super(Character, self).level_up()

        # Recover hp and mp.
        values = {
            "hp": self.prop.max_hp,
            "mp": self.prop.max_mp
        }
        self.set_properties(values)

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description and available commands.
        info = super(Character, self).get_appearance(caller)

        info["max_hp"] = self.prop.max_hp
        info["hp"] = self.prop.hp
        info["max_mp"] = self.prop.max_mp
        info["mp"] = self.prop.mp

        return info

    def get_combat_status(self):
        """
        Get character status used in combats.
        """
        status = super(Character, self).get_combat_status()

        status["max_hp"] = self.prop.max_hp
        status["hp"] = self.prop.hp
        status["max_mp"] = self.prop.max_mp
        status["mp"] = self.prop.mp

        return status

    def is_alive(self):
        """
        Check if the character is alive.

        Returns:
            (boolean) the character is alive or not
        """
        return round(self.prop.hp) > 0

    def provide_exp(self, killer):
        """
        Calculate the exp provide to the killer.
        Args:
            killer: (object) the character who kills it.

        Returns:
            (int) experience give to the killer
        """
        return self.prop.give_exp

    def add_exp(self, exp):
        """
        Add character's exp.
        Args:
            exp: the exp value to add.

        Returns:
            None
        """
        super(Character, self).add_exp(exp)

        self.prop.exp += exp
        while self.prop.exp >= self.prop.max_exp:
            if self.prop.max_exp > 0:
                # can upgrade
                self.prop.exp -= self.prop.max_exp
                self.level_up()
            else:
                # can not upgrade
                self.prop.exp = 0
                break
