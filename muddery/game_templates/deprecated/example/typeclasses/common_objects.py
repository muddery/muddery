"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.utils.localized_strings_handler import _
from muddery.typeclasses.common_objects import MudderyFood, MudderyEquipment


class Food(MudderyFood):
    """
    This is a food. Players can use it to change their properties, such as hp, mp,
    strength, etc.
    """
    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this
            number: (int) the number of the object to use

        Returns:
            (result, number):
                result: (string) a description of the result
                number: (int) actually used number
        """
        if not user:
            raise ValueError("User should not be None.")

        if number <= 0:
            raise ValueError("Number should be above zero.")

        status_changed = False

        result = ""
        used = number
        if used > self.db.number:
            used = self.db.number

        if hasattr(self.cattr, "hp"):
            hp = self.cattr.hp * used

            # recover caller's hp
            recover_hp = int(hp)

            if user.db.hp < 0:
                user.db.hp = 0

            if user.db.hp + recover_hp > user.max_hp:
                recover_hp = user.max_hp - user.db.hp

            # add actual hp value
            if recover_hp > 0:
                user.db.hp += recover_hp
                user.show_status()

            result += _("HP recovered by %s.") % int(recover_hp)

        return result, used
