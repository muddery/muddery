"""
Shop goods is the object in shops. They have some special attributes to record goods information.

"""

from evennia.utils import logger
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.elements.base_element import BaseElement
from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class MudderyShopGoods(BaseElement):
    """
    This is a shop goods. Shops show these objects to players. It contains a common object
    to sell and additional shop information.
    """
    element_type = "SHOP_GOODS"
    element_name = _("Goods", "elements")
    model_name = "shop_goods"

    def set_data(self, data):
        """
        Set goods' data.

        Args:
            data: (record) goods's data.
        """
        self.available = False

        # load goods record
        obj_model_name = ELEMENT("COMMON_OBJECT").model_name

        try:
            obj_record = WorldData.get_table_data(obj_model_name, key=data.goods)
            obj_record = obj_record[0]
            obj_models = ELEMENT_SET.get_class_modeles(obj_record.element_type)
            obj_data = WorldData.get_tables_data(obj_models, key=data.goods)
            obj_data = obj_data[0]
        except Exception as e:
            logger.log_errmsg("Can not find goods %s." % data.goods)
            return

        self.obj_key = data.goods
        self.obj_name = obj_data.name
        self.obj_desc = obj_data.desc
        self.obj_icon = obj_data.icon

        # get price unit information
        try:
            # Get record.
            unit_record = WorldData.get_table_data(obj_model_name, key=data.unit)
            unit_record = unit_record[0]
        except Exception as e:
            logger.log_errmsg("Can not find price unit %s." % data.unit)
            return

        self.unit_key = data.unit
        self.unit_name = unit_record.name

        self.level = data.level
        self.number = data.number
        self.price = data.price
        self.condition = data.condition

        self.available = True

    def is_available(self, caller):
        """
        Is it available to the customer.

        Args:
            caller (obj): the customer.
        """
        if not self.available:
            return False

        return STATEMENT_HANDLER.match_condition(self.condition, caller, None)

    def get_info(self, caller):
        """
        Get the goods' info.

        :param caller:
        :return:
        """
        info = {
            "obj": self.obj_key,
            "level": self.level,
            "name": self.obj_name,
            "desc": self.obj_desc,
            "number": self.number,
            "price": self.price,
            "unit": self.unit_name,
            "icon": self.obj_icon
        }

        return info

    def sell_to(self, caller):
        """
        Buy this goods.

        Args:
            caller: the buyer

        Returns:

        """
        # check price
        unit_number = caller.total_object_number(self.unit_key)
        if unit_number < self.price:
            caller.msg({"alert": _("Sorry, %s is not enough.") % self.unit_name})
            return

        # check if can get these objects
        if not caller.can_get_object(self.obj_key, self.number):
            caller.msg({"alert": _("Sorry, you can not take more %s.") % self.obj_name})
            return

        remove_list = [
            {
                "object_key": self.unit_key,
                "number": self.price
            }
        ]
        receive_list = [
            {
                "object_key": self.obj_key,
                "level": self.level,
                "number": self.number,
            }
        ]

        # Reduce price units and give goods.
        caller.exchange_objects(remove_list, receive_list, show=True)
        caller.msg({"alert": _("Purchase successful!")})

        return
