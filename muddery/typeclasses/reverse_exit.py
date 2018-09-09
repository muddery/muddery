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


class MudderyReverseExit(TYPECLASS("EXIT")):
    """
    This is the reverse side of the two way exit.
    """
    typeclass_key = "REVERSE_EXIT"
    typeclass_name = _("Reverse Exit", "typeclasses")

    def after_data_loaded(self):
        """
        Called after self.data_loaded().
        """
        self.set_name(getattr(self.dfield, "reverse_name", ""))

        # reverse location and destination
        if not self.location:
            self.set_location(getattr(self.dfield, "destination", ""))

        # set exit's destination
        self.set_obj_destination(getattr(self.dfield, "location", ""))

        self.condition = getattr(self.dfield, "condition", "")

        # set icon
        self.set_icon(getattr(self.dfield, "icon", ""))

    def reset_location(self):
        """
        Set object's location to its default location.

        Returns:
            None
        """
        if hasattr(self.dfield, "destination"):
            self.set_location(self.dfield.destination)

