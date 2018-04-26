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
def query_columns(args, request):
    """
    Query all fields of a table.
    """
    if not args or 'table' not in args:
        raise MudderyError(10000, 'Missing argument: "table".')

    return data_query.query_fields(args["table"])


@request_mapping
def query_table(args, request):
    """
    Query all records of a table.
    """
    if not args or 'table' not in args:
        raise MudderyError(10000, 'Missing argument: "table".')

    return data_query.query_table(args["table"])


