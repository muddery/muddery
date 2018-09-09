"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from __future__ import print_function

import traceback
from muddery.utils import utils
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.localized_strings_handler import _
from muddery.mappings.typeclass_set import TYPECLASS
from evennia.utils import logger
from django.conf import settings


class MudderyTwoWayExit(TYPECLASS("EXIT")):
    """
    This is the front side of the two way exit.
    """
    typeclass_key = "TWO_WAY_EXIT"
    typeclass_name = _("Two Way Exit", "typeclasses")
