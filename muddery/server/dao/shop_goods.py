"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class ShopGoods(object):
    """
    Shop's goods.
    """
    table_name = "shop_goods"

    @classmethod
    def get(cls, shop):
        """
        Get properties by typeclass's name.
        """
        return WorldData.get_table_data(cls.table_name, shop=shop)
