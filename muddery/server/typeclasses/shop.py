"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from evennia.utils import logger
from muddery.server.utils.builder import build_object
from muddery.server.mappings.typeclass_set import TYPECLASS
from muddery.server.utils.localized_strings_handler import _
from muddery.worlddata.dao.shop_goods_mapper import SHOP_GOODS


class MudderyShop(TYPECLASS("OBJECT")):
    """
    A shop.
    """
    typeclass_key = "SHOP"
    typeclass_name = _("Shop", "typeclasses")
    model_name = "shops"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        It will be called when swap its typeclass, so it must keep
        old values.
        """
        super(MudderyShop, self).at_object_creation()

        # set default values
        self.db.owner = None

    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.

        All skills, contents will be removed too.
        """
        result = super(MudderyShop, self).at_object_delete()
        if not result:
            return result

        # delete all contents
        for content in self.contents:
            content.delete()

        return True

    def after_data_loaded(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderyShop, self).after_data_loaded()

        # load shop goods
        self.load_goods()
        
        self.verb = getattr(self.system, "verb", None)

    def load_goods(self):
        """
        Load shop goods.
        """
        # shops records
        goods_records = SHOP_GOODS.filter(self.get_data_key())

        goods_keys = set([record.key for record in goods_records])

        # search current goods
        current_goods = set()
        for item in self.contents:
            key = item.get_data_key()
            if key in goods_keys:
                current_goods.add(key)
            else:
                # remove goods that is not in goods_keys
                item.delete()

        # add new goods
        for goods_record in goods_records:
            goods_key = goods_record.key
            if goods_key not in current_goods:
                # Create shop_goods object.
                goods_obj = build_object(goods_key)
                if not goods_obj:
                    logger.log_errmsg("Can't create goods: %s" % goods_key)
                    continue

                goods_obj.move_to(self, quiet=True)

    def set_owner(self, owner):
        """
        Set the owner of the shop.

        :param owner:
        :return:
        """
        self.db.owner = owner

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
        info = {
            "dbref": self.dbref,
            "name": self.get_name(),
            "desc": self.db.desc
        }

        icon = self.icon
        if not icon and self.db.owner:
            icon = self.db.owner.icon
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
                     "unit": item.unit_name,
                     "icon": item.icon}
            
            goods_list.append(goods)

        return goods_list
