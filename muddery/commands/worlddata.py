"""
Commands

Add three commands: @importdata, @datainfo and @batchbuilder

"""

import os
from django.conf import settings
from django.db.models.loading import get_model
from muddery.utils.importer import import_model, import_all
from muddery.utils.builder import build_all
from muddery.utils.exception import MudderyError
from evennia import default_cmds
from evennia.utils import logger
import traceback

#------------------------------------------------------------
# import data tables
#------------------------------------------------------------
class CmdImportData(default_cmds.MuxCommand):
    """
    Usage:
      @importdata

      If <modelname> is empty, it will import all data files in settings.OBJECT_DATA_MODELS.
    """
    key = "@importdata"
    locks = "perm(Builders)"
    help_cateogory = "Builders"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"

        caller = self.caller

        # count the number of files loaded
        count = 0

        # get model_name, can specify the model name in args
        # if no args is given, load all models in settings.OBJECT_DATA_MODELS
        models = self.args
        if models:
            models = [arg.strip() for arg in models.split(',')]
        else:
            models = settings.OBJECT_DATA_MODELS + settings.OTHER_DATA_MODELS

        # import models one by one
        for model_name in models:
            try:
                import_model(model_name)
                caller.msg("%s imported." % model_name)
                count += 1
            except MudderyError, e:
                caller.msg(e)
                continue
            except Exception, e:
                caller.msg("Can not import %s." % model_name)
                continue

        caller.msg("Total %d files imported." % count)


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
            import_all()
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
