"""
Matter

Matters can be seen in a room or in an area.

"""

import asyncio
from muddery.server.utils.logger import logger
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.image_resource import ImageResource
from muddery.server.database.worlddata.world_rooms import WorldRooms
from muddery.server.database.worlddata.worlddata import WorldData


class MudderyMatter(BaseElement):
    """
    Material objects can be seen in a room or in an area.
    """
    element_type = "MATTER"
    element_name = "Matter"
    model_name = ""

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyMatter, self).__init__()

        self.name = None
        self.desc = None
        self.icon = None

    async def at_element_setup(self, first_time):
        """
        Init the character.
        """
        await super(MudderyMatter, self).at_element_setup(first_time)

        self.set_name(self.const.name)
        self.set_desc(self.const.desc)
        self.set_icon(self.const.icon)

    def get_appearance(self):
        """
        The common appearance for all players.
        """
        info = {
            "key": self.get_element_key(),
            "name": self.get_name(),
            "desc": self.get_desc(),
            "icon": self.get_icon(),
        }

        return info

    async def get_detail_appearance(self, caller):
        """
        The particular appearance for the caller.
        """
        info = self.get_appearance()
        details = await asyncio.gather(
            self.get_conditional_desc(caller),
            self.get_available_commands(caller),
        )
        info["desc"] = details[0]
        info["cmds"] = details[1]

        return info

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        return []

    def set_name(self, name):
        """
        Set object's name.

        Args:
        name: (string) Name of the object.
        """
        self.name = name

    def get_name(self):
        """
        Get player character's name.
        """
        return self.name

    def set_desc(self, desc):
        """
        Set object's description.

        Args:
        desc: (string) Description.
        """
        self.desc = desc

    def get_desc(self):
        """
        Get the element's description.
        :return:
        """
        return self.desc

    async def get_conditional_desc(self, caller):
        """
        The particular description for the caller.
        """
        return self.get_desc()

    def set_icon(self, icon_key):
        """
        Set object's icon.
        Args:
            icon_key: (String)icon's resource key.

        Returns:
            None
        """
        self.icon = icon_key

    def get_icon(self):
        """
        Get object's icon.
        :return:
        """
        return self.icon
