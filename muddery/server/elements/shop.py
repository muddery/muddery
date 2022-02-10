"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.database.worlddata.shop_goods import ShopGoods
from muddery.common.utils.utils import async_gather


class MudderyShop(ELEMENT("MATTER")):
    """
    A shop.
    """
    element_type = "SHOP"
    element_name = "Shop"
    model_name = "shops"

    async def at_element_setup(self, first_time):
        """
        Set data_info to the object.

        Returns:
            None
        """
        await super(MudderyShop, self).at_element_setup(first_time)

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
                self.set_icon(owner.get_icon())

    def load_goods(self):
        """
        Load shop goods.
        :return:
        """
        goods_data = ShopGoods.get_by_shop(self.get_element_key())

        self.goods = []
        for item in goods_data:
            goods = ELEMENT("SHOP_GOODS")()
            goods.set_data(item)
            self.goods.append(goods)

    async def get_detail_appearance(self, caller):
        """
        Get shop information.

        Args:
            caller (obj): the custom
        """
        info = await super(MudderyShop, self).get_detail_appearance(caller)

        goods_list = []
        if self.goods:
            is_available = await async_gather([item.is_available(caller) for item in self.goods])
            available_goods = [index for index in range(len(self.goods)) if is_available[index]]

            if available_goods:
                goods_list = await async_gather([self.goods[index].get_info(caller) for index in available_goods])
                for index, item in enumerate(goods_list):
                    item["index"] = available_goods[index]

        info["goods"] = goods_list
        return info

    def get_verb(self):
        """
        Get the action name of opening the shop.
        :return:
        """
        return self.const.verb if self.const.verb else self.const.name

    async def is_available(self, caller):
        """
        Is it available to the customer.

        Args:
            caller (obj): the customer.
        """
        if not self.const.condition:
            return True

        return await STATEMENT_HANDLER.match_condition(self.const.condition, caller, None)

    async def sell_goods(self, goods_index, caller):
        """
        Sell goods to the caller.
        :param goods_index:
        :param caller:
        :return:
        """
        await self.goods[goods_index].sell_to(caller)
