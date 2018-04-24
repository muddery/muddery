"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.dao import common_mapper
from muddery.worlddata.utils import utils


def query_fields(model_name):
    """
    Query table's data.
    """
    return common_mapper.get_all_fields(model_name)


def query_table(model_name):
    """
    Query table's data.
    """
    return common_mapper.get_all_records_lines(model_name)
