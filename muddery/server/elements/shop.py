"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from evennia.utils import logger
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.database.worlddata.shop_goods import ShopGoods
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.elements.base_element import BaseElement


class MudderyShop(BaseElement):
    """
    A shop.
    """
    element_type = "SHOP"
    element_name = _("Shop", "elements")
    model_name = "shops"

    def at_element_setup(self, first_time):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderyShop, self).at_element_setup(first_time)

        # load shop goods
        self.load_goods()

    def set_owner(self, owner):
        """
        Set the shop's owner.
        :param owner:
        :return:
        """
        if owner:
            if not self.const.icon:
                self.const_data_handler.add("icon", owner.get_icon())

    def load_goods(self):
        """
        Load shop goods.
        :return:
        """
        goods_data = ShopGoods.get_by_shop(self.element_key)

        self.goods = []
        for item in goods_data:
            goods = ELEMENT("SHOP_GOODS")()
            goods.set_data(item)
            self.goods.append(goods)

    def get_info(self, caller):
        """
        Get shop information.

        Args:
            caller (obj): the custom
        """
        info = {
            "key": self.element_key,
            "name": self.const.name,
            "desc": self.const.desc,
            "icon": self.const.icon,
            "goods": [],
        }

        for index, item in enumerate(self.goods):
            if item.is_available(caller):
                goods = item.get_info(caller)
                goods["index"] = index
                info["goods"].append(goods)

        return info

    def get_verb(self):
        """
        Get the action name of opening the shop.
        :return:
        """
        return self.const.verb if self.const.verb else self.const.name

    def is_available(self, caller):
        """
        Is it available to the customer.

        Args:
            caller (obj): the customer.
        """
        if not self.const.condition:
            return True

        return STATEMENT_HANDLER.match_condition(self.const.condition, caller, None)

    def sell_goods(self, goods_index, caller):
        """
        Sell goods to the caller.
        :param goods_index:
        :param caller:
        :return:
        """
        self.goods[goods_index].sell_to(caller)
