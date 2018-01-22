"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

from muddery.typeclasses.characters import MudderyCharacter


class Character(MudderyCharacter):
    """
    Custom character class.

    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(Character, self).at_object_creation()

        # Set default values.
        if not self.attributes.has("mp"):
            self.db.mp = 1
        if not self.attributes.has("sp"):
            self.db.sp = 1

    def after_data_key_changed(self):
        """
        Called at data_key changed.
        """
        super(Character, self).after_data_key_changed()

        # Reset values.
        self.db.mp = self.max_mp
        self.db.sp = self.max_sp
        
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
        