"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

from muddery.typeclasses.character import MudderyCharacter


class Character(MudderyCharacter):
    """
    Custom character class.

    """
    key = "CHARACTER"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(Character, self).at_object_creation()

        # Set default values.
        if not self.attributes.has("mp"):
            self.db.mp = 0
        if not self.attributes.has("sp"):
            self.db.sp = 0

    def after_data_key_changed(self):
        """
        Called at data_key changed.
        """
        super(Character, self).after_data_key_changed()

        # Reset values.
        self.db.mp = self.max_mp
        self.db.sp = self.max_sp

    def load_model_data(self):
        """
        Load character's level data.
        """
        super(Character, self).load_model_data()

        self.max_mp = getattr(self.dfield, "max_mp", 0)
        self.max_sp = getattr(self.dfield, "max_sp", 0)

    def reborn(self):
        """
        Reborn after being killed.
        """
        super(Character, self).reborn()
        
        # Recover mp and sp.
        self.db.mp = self.max_mp
        self.db.sp = self.max_sp
        
    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        super(Character, self).level_up()

        # Recover mp and sp.
        self.db.mp = self.max_mp
        self.db.sp = self.max_sp

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description and available commands.
        info = super(Character, self).get_appearance(caller)
        info["max_mp"] = self.max_mp
        info["mp"] = self.db.mp

        return info

    def get_combat_status(self):
        """
        Get character status used in combats.
        """
        status = super(Character, self).get_combat_status()

        status["max_mp"] = self.max_mp
        status["mp"] = self.db.mp

        return status
