"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from evennia.utils import logger, create
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.builder import build_object, get_object_record
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS


class MudderyShop(MudderyObject):
    """
    A shop.
    """
    def load_data(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderyShop, self).load_data()
        
        # load shop goods
        self.load_goods()
        
        self.verb = getattr(self.dfield, "verb", None)

    def load_goods(self):
        """
        Load shop goods.
        """
        # shops records
        goods_records = DATA_SETS.shop_goods.objects.filter(shop=self.get_data_key())

        goods_keys = set([record.goods for record in goods_records])

        # search current goods
        current_goods = set()
        for item in self.contents:
            key = item.get_goods_key()
            if key in goods_keys:
                current_goods.add(key)
            else:
                # remove this goods
                item.delete()

        # add new goods

        # get typeclass model
        for goods_record in goods_records:
            goods_key = goods_record.goods
            if goods_key not in current_goods:
                # Create goods object.

                typeclass = None
                try:
                    typeclass = DATA_SETS.typeclasses.objects.get(key=goods_record.typeclass)
                except Exception, e:
                    logger.log_errmsg("Can't create goods: %s" % goods_key)
                    continue

                goods_obj = create.create_object(typeclass.path, goods_record.goods)
                if not goods_obj:
                    logger.log_errmsg("Can't create goods: %s" % goods_key)
                    continue

                goods_obj.set_goods_key(self.get_data_key(), goods_key)
                goods_obj.move_to(self, quiet=True)

    def show_shop(self, caller):
        """
        Send shop data to the caller.
        """
        if not caller:
            return

        info = self.return_shop_info()
        caller.msg({"shop": info})

    def return_shop_info(self):
        """
        Get shop information.
        """
        info = {"dbref": self.dbref,
                "name": self.get_name(),
                "desc": self.db.desc}

        icon = getattr(self, "icon", None)
        if icon:
            info["icon"] = icon

        goods_list = self.return_shop_goods()
        info["goods"] = goods_list
            
        return info
                
    def return_shop_goods(self):
        """
        Get shop's information.
        """
        goods_list = []

        # Get shop goods
        for item in self.contents:
            if not item.available:
                continue

            goods = {"dbref": item.dbref,
                     "name": item.name,
                     "desc": item.desc,
                     "number": item.number,
                     "price": item.price,
                     "unit": item.unit_name}

            if item.icon:
                goods["icon"] = item.icon
            
            goods_list.append(goods)

        return goods_list
