"""
Query and deal common tables.
"""

from muddery.server.database.dao.base_query import BaseQuery
from muddery.server.database.dao.worlddata import WorldData


class ShopGoods(BaseQuery):
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
