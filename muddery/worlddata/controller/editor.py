"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.request_mapping import request_mapping
from muddery.worlddata.service import data_query
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError


@request_mapping
def query_table(args):
    """
    Query a table.
    """
    if 'table' not in args:
        raise MudderyError(10000, "Lost a table name.")

    return data_query.query_table(args["table"])


@request_mapping
def query_all_skills(args):
    """
    Query all skills.
    """
    return data_query.query_table("skills")

