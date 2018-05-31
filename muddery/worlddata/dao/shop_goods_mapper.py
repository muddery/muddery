"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class ShopGoodsMapper(object):
    """
    Shop's goods.
    """
    def __init__(self):
        self.model_name = "shop_goods"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get(self, shop):
        """
        Get shop's goods

        Args:
            shop: (string) shop's key.
        """
        return self.objects.filter(shop=shop)


SHOP_GOODS = ShopGoodsMapper()
