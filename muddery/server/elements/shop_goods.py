"""
Shop goods is the object in shops. They have some special attributes to record goods information.

"""

from evennia.utils import logger
from muddery.server.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET


class MudderyShopGoods(ELEMENT("OBJECT")):
    """
    This is a shop goods. Shops show these objects to players. It contains a common object
    to sell and additional shop information.
    """
    element_key = "SHOP_GOODS"
    element_name = _("Goods", "elements")
    model_name = "shop_goods"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        super(MudderyShopGoods, self).at_object_creation()

        self.available = False

    def after_data_loaded(self):
        """
        Load goods data.

        Returns:
            None
        """
        super(MudderyShopGoods, self).after_data_loaded()

        self.available = False

        self.shop_key = self.data.shop
        self.goods_key = self.data.goods
        self.goods_level = self.data.level if self.data.level else 0

        # set goods information
        self.price = self.data.price if self.data.price else 0
        self.unit_key = self.data.unit
        self.number = self.data.number if self.data.number else 0
        self.condition = self.data.condition

        # get price unit information
        try:
            # Get record.
            obj_model_name = ELEMENT("OBJECT").model_name
            unit_record = WorldData.get_table_data(obj_model_name, key=self.unit_key)
            unit_record = unit_record[0]
        except Exception as e:
            logger.log_errmsg("Can not find %s's price unit %s." % (self.goods_key, self.unit_key))
            return

        self.unit_name = unit_record.name

        # load goods
        try:
            obj_record = WorldData.get_table_data(obj_model_name, key=self.goods_key)
            obj_record = obj_record[0]
            goods_models = ELEMENT_SET.get_class_modeles(obj_record.typeclass)
            goods_data = WorldData.get_tables_data(goods_models, key=self.goods_key)
            goods_data = goods_data[0]
        except Exception as e:
            logger.log_errmsg("Can not find goods %s." % self.goods_key)
            return

        self.name = goods_data.name
        self.desc = goods_data.desc
        self.icon = goods_data.icon

        self.available = True
        
    def is_available(self, caller):
        """
        Is it available to the customer.

        Args:
            caller (obj): the customer.
        """
        if not self.available:
            return False

        return self.is_visible(caller)

    def sell_to(self, caller):
        """
        Buy this goods.

        Args:
            caller: the buyer

        Returns:

        """
        # check price
        unit_number = caller.get_object_number(self.unit_key)
        if unit_number < self.price:
            caller.msg({"alert": _("Sorry, %s is not enough.") % self.unit_name})
            return

        # check if can get these objects
        if not caller.can_get_object(self.goods_key, self.number):
            caller.msg({"alert": _("Sorry, you can not take more %s.") % self.name})
            return

        remove_list = [
            {
                "object": self.unit_key,
                "number": self.price
            }
        ]
        receive_list = [
            {
                "object": self.goods_key,
                "number": self.number
            }
        ]

        try:
            # Reduce price units and give goods.
            caller.exchange_objects(remove_list, receive_list)
        except Exception as e:
            logger.log_errmsg("Can not buy goods %s: %s" % (self.goods_key, e))
            caller.msg({"alert": _("Sorry, you can not buy %s.") % self.name})

        return
