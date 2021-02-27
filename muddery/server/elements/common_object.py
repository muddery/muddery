"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.server.utils.exception import MudderyError
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class MudderyCommonObject(ELEMENT("OBJECT")):
    """
    This is a common object. Players can put it in their inventories.
    
    There can be a lot of common objects of the same kind in the game, so their haven't
    home and fixed locations.
    
    It has two additional properties: max_stack(int) and unique(bool). They decide the number
    of the object that a player can put in his inventory.
    """
    element_type = "COMMON_OBJECT"
    element_name = _("Common Object", "elements")
    model_name = "common_objects"

    def after_data_loaded(self):
        """
        Initial this object.
        """
        super(MudderyCommonObject, self).after_data_loaded()

        # set object stack info
        self.max_stack = self.const.max_stack if self.const.max_stack else 1
        self.unique = self.const.unique
        self.can_remove = self.const.can_remove
        self.can_discard = self.const.can_discard

#    def increase_num(self, number):
#        """
#        Increase object's number.
#        """
#        if number == 0:
#            return
#
#        if number < 0:
#            raise MudderyError("%s can not increase a negative nubmer." % self.get_data_key())#
#
#        if self.max_stack == 1 and self.states.number == 1:
#            raise MudderyError("%s can not stack." % self.get_data_key())
#
#        if self.states.number + number > self.max_stack:
#            raise MudderyError("%s over stack." % self.get_data_key())
#
#        self.states.number += number
#        return
#
#    def decrease_num(self, number):
#        """
#        Decrease object's number.
#        """
#        if number == 0:
#            return
#
#        if number < 0:
#            raise MudderyError("%s can not decrease a negative nubmer." % self.get_data_key())
#
#        if self.states.number < number:
#            raise MudderyError("%s's number will below zero." % self.get_data_key())
#
#        self.states.number -= number
#        return

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # Get name, description and available commands.
        info = super(MudderyCommonObject, self).get_appearance(caller)

        info["can_remove"] = self.can_remove
        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.can_discard:
            commands.append({
                "name": _("Discard"),
                "cmd": "discard",
                "args": self.dbref,
                "confirm": _("Discard this object?"),
            })
        return commands

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this

        Returns:
            result: (string) a description of the result
        """
        return _("No effect."), 0


class MudderyFood(ELEMENT("COMMON_OBJECT")):
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

        values_merge = {key: self.const_data_handler.get(key) for key, info in self.get_properties_info().items() if
                        not info["mutable"]}
        values_merge.update(self.states.all())

        changes = {}
        new_states = {}
        for key, increment in values_merge.items():
            if not increment:
                continue

            increment *= number

            if user.states.has(key):
                current_value = user.states.load(key)
                new_value = user.validate_property(key, current_value + increment)
                changes[key] = new_value - current_value
                if new_value != current_value:
                    new_states[key] = new_value
            elif user.const_data_handler.has(key):
                current_value = user.const_data_handler.get(key)
                new_value = user.validate_property(key, current_value + increment)
                changes[key] = new_value - current_value
                user.const_data_handler.add(key, new_value)

        if new_states:
            user.states.saves(new_states)

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
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = [{"name": _("Use"), "cmd": "use", "args": self.dbref}]
        commands.extend(super(MudderyFood, self).get_available_commands(caller))

        return commands


class MudderyEquipment(ELEMENT("COMMON_OBJECT")):
    """
    This is a equipment. Players can equip it to change their properties, such as attack, defence,
    etc.
    """
    element_type = "EQUIPMENT"
    element_name = _("Equipment", "elements")
    model_name = "equipments"

    def after_data_loaded(self):
        """
        Load equipments data.
        """
        super(MudderyEquipment, self).after_data_loaded()

        self.type = self.const.type
        self.position = self.const.position

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

        values_merge = {key: self.const_data_handler.get(key) for key, info in self.get_properties_info().items() if
                        not info["mutable"]}
        values_merge.update(self.states.all())

        changes = {}
        new_states = {}
        for key, increment in values_merge.items():
            if not increment:
                continue

            if user.states.has(key):
                current_value = user.states.load(key)
                new_value = user.validate_property(key, current_value + increment)
                changes[key] = new_value - current_value
                if new_value != current_value:
                    new_states[key] = new_value
            elif user.const_data_handler.has(key):
                current_value = user.const_data_handler.get(key)
                new_value = user.validate_property(key, current_value + increment)
                changes[key] = new_value - current_value
                user.const_data_handler.add(key, new_value)

        if new_states:
            user.states.saves(new_states)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = [{
            "name": _("Equip"),
            "cmd": "equip",
            "args": self.dbref
        }]

        # Can not discard when equipped
        if self.can_discard:
            commands.append({
                "name": _("Discard"),
                "cmd": "discard",
                "args": self.dbref,
                "confirm": _("Discard this object?"),
            })

        return commands


class MudderySkillBook(ELEMENT("COMMON_OBJECT")):
    """
    This is a skill book. Players can use it to learn a new skill.
    """
    element_type = "SKILL_BOOK"
    element_name = _("Skill Book", "elements")
    model_name = "skill_books"

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = [{"name": _("Use"), "cmd": "use", "args": self.dbref}]
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
        if not skill_key:
            return _("No effect."), 0

        if user.learn_skill(skill_key, False, False):
            return _("You learned skill."), 1
        else:
            return _("No effect."), 0

