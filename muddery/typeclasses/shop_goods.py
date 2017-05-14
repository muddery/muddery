"""
Shop goods is the object in shops. They have some special attributes to record goods information.

"""

from django.conf import settings
from django.apps import apps
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.builder import build_object, get_object_record
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.data_sets import DATA_SETS


class MudderyShopGoods(MudderyObject):
    """
    This is a shop goods. Shops show these objects to players. It contains a common object
    to sell and additional shop information.
    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        super(MudderyShopGoods, self).at_object_creation()

        # Set default values.
        if not self.attributes.has("goods"):
            self.db.goods = None

        self.available = False

    def after_data_loaded(self):
        """
        Load goods data.

        Returns:
            None
        """
        self.available = False

        self.shop_key = getattr(self.dfield, "shop", "")
        self.goods_key = getattr(self.dfield, "goods", "")

        if not self.shop_key or not self.goods_key:
            if self.db.goods:
                self.db.goods.delete()
                self.db.goods = None
            return

        # set goods information
        self.price = getattr(self.dfield, "price", 0)
        self.unit_key = getattr(self.dfield, "unit", "")
        self.number = getattr(self.dfield, "number", 0)
        self.condition = getattr(self.dfield, "condition", "")

        # get price unit information
        unit_record = get_object_record(self.unit_key)
        if not unit_record:
            logger.log_errmsg("Can not find %s price unit %s." % (self.goods_key, self.unit_key))
            return
        self.unit_name = unit_record.name

        # load goods object
        goods = self.db.goods
        if goods:
            if goods.get_data_key() == self.goods_key:
                goods.load_data()
            else:
                goods.set_data_key(self.goods_key)
        else:
            goods = build_object(self.goods_key)
            if goods:
                self.db.goods = goods
            else:
                logger.log_err("Can not create goods %s." % self.goods_key)
                return

        self.name = goods.get_name()
        self.desc = goods.db.desc
        self.icon = getattr(goods, "icon", None)

        self.available = True

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
        if not caller.can_get_object(self.db.goods.get_data_key(), self.number):
            caller.msg({"alert": _("Sorry, you can not take more %s.") % self.db.goods.get_name()})
            return

        # Reduce price units.
        if not caller.remove_object(self.unit_key, self.price):
            caller.msg({"alert": _("Sorry, %s is not enough.") % self.unit_name})
            return

        # Give goods.
        obj_list = [{"object": self.db.goods.get_data_key(),
                     "number": self.number}]
        caller.receive_objects(obj_list)
