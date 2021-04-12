"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.server.utils.exception import MudderyError
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.elements.base_element import BaseElement
from muddery.server.utils.localized_strings_handler import _


class MudderyCommonObject(BaseElement):
    """
    This is a common object, the base class of all objects..
    """
    element_type = "COMMON_OBJECT"
    element_name = _("Common Object", "elements")
    model_name = "common_objects"

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
        info = {
            "name": self.get_name(),
            "desc": self.get_desc(),
            "icon": self.get_icon(),
            "cmds": self.get_available_commands(caller),
        }
        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        return []
