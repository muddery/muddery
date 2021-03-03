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
        Get properties by element_type's name.
        """
        return WorldData.get_table_data(cls.table_name, shop=shop)
