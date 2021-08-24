"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class ShopGoods(BaseQuery):
    """
    Shop's goods.
    """
    table_name = "shop_goods"

    @classmethod
    def get_by_shop(cls, shop):
        """
        Get properties by the shop's element_type.
        """
        return WorldData.get_table_data(cls.table_name, shop=shop)

    @classmethod
    def get_by_goods(cls, goods):
        """
        Get properties by the goods' element_type.
        """
        return WorldData.get_table_data(cls.table_name, goods=goods)
