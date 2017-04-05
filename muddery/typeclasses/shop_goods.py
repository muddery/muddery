"""
Shop goods is the object in shops. They have some special attributes to record goods information.

"""

from django.conf import settings
from django.apps import apps
from evennia.objects.objects import DefaultObject
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.builder import build_object, get_object_record
from muddery.utils.localized_strings_handler import LS
from muddery.worlddata.data_sets import DATA_SETS


class MudderyShopGoods(DefaultObject):
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
        self.db.shop_key = None
        self.db.goods_key = None
        self.db.goods = None

        self.available = False

    def at_init(self):
        """
        Load goods data.
        """
        super(MudderyShopGoods, self).at_init()

        # need save before modify m2m fields
        self.save()

        self.available = False

        try:
            # Load db data.
            self.load_data()
        except Exception, e:
            logger.log_tracemsg("%s can not load data:%s" % (self.dbref, e))
            return

    def load_data(self):
        """
        Load goods data.

        Returns:
            None
        """
        if not self.db.shop_key or not self.db.goods_key:
            if self.db.goods:
                self.db.goods.delete()
                self.db.goods = None
            return

        shop_key = self.db.shop_key
        goods_key = self.db.goods_key

        # Get goods record.
        goods_record = None
        try:
            # Get records.
            goods_record = DATA_SETS.shop_goods.objects.get(shop=shop_key, goods=goods_key)
        except Exception, e:
            logger.log_errmsg("Can not find goods %s in shop %s: %s" % (goods_key, shop_key, e))
            return

        # get price unit information
        unit_record = get_object_record(goods_record.unit)
        if not unit_record:
            logger.log_errmsg("Can not find %s price unit %s." % (goods_key, goods_record.unit))
            return
        unit_name = unit_record.name

        # load goods object
        goods = self.db.goods
        if goods:
            if goods.get_data_key == goods_key:
                goods.load_data()
            else:
                goods.set_data_key(goods_key)
        else:
            goods = build_object(goods_key)
            if goods:
                self.db.goods = goods
            else:
                logger.log_err("Can not create goods %s." % goods_key)
                return

        # set goods information
        self.price = goods_record.price
        self.unit_key = goods_record.unit
        self.unit_name = unit_name
        self.number = goods_record.number
        self.condition = goods_record.condition

        self.name = goods.get_name()
        self.desc = goods.db.desc
        self.icon = getattr(goods, "icon", None)

        self.available = True

    def set_goods_key(self, shop_key, goods_key):
        """
        Set goods keys.

        Args:
            shop_key: (String) The key of the shop.
            goods_key: (String) The key of this goods.

        Returns:
            None
        """
        if shop_key == self.db.shop_key and goods_key == self.db.goods_key:
            return

        self.db.shop_key = shop_key
        self.db.goods_key = goods_key

        self.load_data()

    def get_goods_key(self):
        """
        Get the key of the goods.

        Returns:
            String: key
        """
        return self.db.goods_key

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
            caller.msg({"alert": LS("Sorry, %s is not enough.") % self.unit_name})
            return

        # check if can get these objects
        if not caller.can_get_object(self.db.goods.get_data_key(), self.number):
            caller.msg({"alert": LS("Sorry, you can not take more %s.") % self.db.goods.get_name()})
            return

        # Reduce price units.
        if not caller.remove_object(self.unit_key, self.price):
            caller.msg({"alert": LS("Sorry, %s is not enough.") % self.unit_name})
            return

        # Give goods.
        obj_list = [{"object": self.db.goods.get_data_key(),
                     "number": self.number}]
        caller.receive_objects(obj_list)
