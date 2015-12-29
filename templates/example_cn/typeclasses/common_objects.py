"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.utils.localized_strings_handler import LS
from muddery.typeclasses.common_objects import MudderyCommonObject
from muddery.typeclasses.common_objects import MudderyFood
from muddery.typeclasses.common_objects import MudderyEquipment


class CommonObject(MudderyCommonObject):
    """
    """
    pass


class Equipment(MudderyEquipment):
    """
    """
    pass


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

        if hasattr(self.dfield, "hp"):
            recover_hp = user.add_hp(self.dfield.hp * used)
            if recover_hp > 0:
                status_changed = True
            result += LS("HP recovered by %s.") % int(recover_hp)

        if status_changed:
            user.show_status()

        return result, used
