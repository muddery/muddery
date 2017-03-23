"""
Commands

Add three commands: @importdata, @datainfo and @batchbuilder

"""

import os
from django.conf import settings
from muddery.utils.importer import import_model, import_local_all
from muddery.utils.builder import build_all
from muddery.utils.exception import MudderyError
from evennia import default_cmds
from evennia.utils import logger
import traceback


#------------------------------------------------------------
# load world
#------------------------------------------------------------
class CmdLoadWorld(default_cmds.MuxCommand):
    """
    Usage:
      @loadworld

    Build the whole game world with data in files.
    """
    key = "@loadworld"
    locks = "perm(Builders)"
    help_cateogory = "Builders"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"
        caller = self.caller

        try:
            import_local_all()
            build_all(caller)
        except Exception, e:
            ostring = "Can't build world: %s" % e
            caller.msg(ostring)
            logger.log_tracemsg(ostring)


#------------------------------------------------------------
# build world
#------------------------------------------------------------
class CmdBuildWorld(default_cmds.MuxCommand):
    """
    Usage:
      @buildworld

    Build the whole game world with data in files.
    """
    key = "@buildworld"
    locks = "perm(Builders)"
    help_cateogory = "Builders"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"
        caller = self.caller

        try:
            build_all(caller)
        except Exception, e:
            ostring = "Can't build world: %s" % e
            caller.msg(ostring)
            logger.log_tracemsg(ostring)
