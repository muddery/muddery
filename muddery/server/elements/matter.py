"""
Matter

Matters can be seen in a room or in an area.

"""

from muddery.server.utils.logger import logger
from muddery.server.elements.base_element import BaseElement
from muddery.server.database.worlddata.conditional_desc import ConditionalDesc
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.common.utils.utils import async_gather


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
        level, desc, cmds = await async_gather([
            self.get_level(),
            self.get_conditional_desc(caller),
            self.get_available_commands(caller),
        ])

        info["level"] = level
        info["cmds"] = cmds

        if desc:
            info["desc"] = desc

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
        records = ConditionalDesc.get_data(self.element_type, self.get_element_key())
        if records:
            items = [(r.condition, r.desc) for r in records]
            results = await async_gather([
                STATEMENT_HANDLER.match_condition(item[0], caller, self) for item in items
            ])
            for i, result in enumerate(results):
                if result:
                    return items[i][1]

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
