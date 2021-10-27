"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class MudderyPocketObject(ELEMENT("COMMON_OBJECT")):
    """
    This is a pocket object. Players can put it in their inventories.
    
    There can be a lot of pocket objects of the same kind in the game, so their haven't
    home and fixed locations.
    
    It has two additional properties: max_stack(int) and unique(bool). They decide the number
    of the object that a player can put in his inventory.
    """
    element_type = "POCKET_OBJECT"
    element_name = _("Pocket Object", "elements")
    model_name = "pocket_objects"

    def get_name(self):
        """
        Get the element's name.
        :return:
        """
        return self.const.name

    def get_desc(self):
        """
        Get the element's description.
        :return:
        """
        return self.const.desc

    def get_icon(self):
        """
        Get the element's icon.
        :return:
        """
        return self.const.icon

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # Get name, description and available commands.
        info = super(MudderyPocketObject, self).get_appearance(caller)
        info["can_remove"] = self.const.can_remove
        info["can_discard"] = self.const.can_discard

        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        return super(MudderyPocketObject, self).get_available_commands(caller)

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this

        Returns:
            result: (string) a description of the result
        """
        return _("No effect."), 0

    def can_discard(self):
        """
        Can discard this object from the inventory. Default is True.
        :return:
        """
        if self.const_data_handler.has("can_discard"):
            return self.const.can_discard

        return True


class MudderyFood(ELEMENT("POCKET_OBJECT")):
    """
    This is a food. Players can use it to change their properties, such as hp, mp,
    strength, etc.
    """
    element_type = "FOOD"
    element_name = _("Food", "elements")
    model_name = "foods"

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this

        Returns:
            result: (string) a description of the result
        """
        if not user:
            raise ValueError("User should not be None.")

        if not number:
            return

        properties = {key: self.const_data_handler.get(key) for key, info in self.get_properties_info().items()}
        to_change = {key: value * number for key, value in properties.items() if value != 0}
        changes = user.change_states(to_change)
        user.show_status()

        results = []
        properties_info = self.get_properties_info()
        for key in changes:
            if key in properties_info:
                # set result
                attribute_info = properties_info.get(key)
                signal = '+' if changes[key] >= 0 else ''
                results.append("%s %s%s" % (attribute_info["name"], signal, changes[key]))

        return ", ".join(results), number

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = [{
            "name": _("Use"),
            "cmd": "use",
        }]
        commands.extend(super(MudderyFood, self).get_available_commands(caller))

        return commands


class MudderyEquipment(ELEMENT("POCKET_OBJECT")):
    """
    This is a equipment. Players can equip it to change their properties, such as attack, defence,
    etc.
    """
    element_type = "EQUIPMENT"
    element_name = _("Equipment", "elements")
    model_name = "equipments"

    def get_body_position(self):
        """
        Get the body position to equip this equipment.
        :return:
        """
        return self.const.position

    def equip_to(self, user):
        """
        Equip this equipment to the user. It is called when a character equip
        this equipment.

        This implementation uses the simplest way to add equipment effects to
        the user. It simply add equipment's effect fields to the user. The user
        must has attributes that has the same name as the equipment's effects.
        You can implementation this method in another way.

        Args:
            user: (object) the user of the equipment.

        Returns:
            None
        """
        if not user:
            return

        properties = {key: self.const_data_handler.get(key) for key, info in self.get_properties_info().items()}
        to_change = {key: value for key, value in properties.items() if value != 0}
        user.change_const_properties(to_change)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = [{
            "name": _("Equip"),
            "cmd": "equip",
        }]
        commands.extend(super(MudderyEquipment, self).get_available_commands(caller))

        return commands


class MudderySkillBook(ELEMENT("POCKET_OBJECT")):
    """
    This is a skill book. Players can use it to learn a new skill.
    """
    element_type = "SKILL_BOOK"
    element_name = _("Skill Book", "elements")
    model_name = "skill_books"

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = [{
            "name": _("Use"),
            "cmd": "use",
        }]
        commands.extend(super(MudderySkillBook, self).get_available_commands(caller))

        return commands

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this

        Returns:
            result: (string) a description of the result
        """
        if not user:
            raise ValueError("User should not be None.")

        skill_key = self.const.skill
        skill_level = self.const.level
        if not skill_key:
            return _("No effect."), 0

        try:
            user.learn_skill(skill_key, skill_level, False)
            return _("You learned skill."), 1
        except:
            return _("No effect."), 0

