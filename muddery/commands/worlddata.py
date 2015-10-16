"""
Commands

Add three commands: @importdata, @datainfo and @batchbuilder

"""

import os
from django.conf import settings
from django.db.models.loading import get_model
from muddery.utils.importer import import_file, import_all
from muddery.utils.builder import build_all
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
            models = [model for data_models in settings.OBJECT_DATA_MODELS
                      for model in data_models]
            models += [model for model in settings.OTHER_DATA_MODELS]

		# get file's extension name
        file_type = settings.WORLD_DATA_FILE_TYPE.lower()
        ext_name = ""
        if file_type == "csv":
            ext_name = ".csv"
        else:
            caller.msg("Does not support file type %s." % settings.WORLD_DATA_FILE_TYPE)
            caller.msg("Total %d files imported." % count)
            return

        # import models one by one
        for model_name in models:
            # make file name
            file_name = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER, model_name + ext_name)

            # import data
            try:
                import_file(file_name, model_name)
                caller.msg("%s imported." % model_name)
                count += 1
            except Exception, e:
                caller.msg("Can not import %s." % model_name)
                continue

        caller.msg("Total %d files imported." % count)


#------------------------------------------------------------
# set object's data model and data key
#------------------------------------------------------------
class CmdSetDataInfo(default_cmds.MuxCommand):
    """
    Usage:
    @datainfo <obj>[=<key>]

    This will set the data key to an object.
    @datainfo <obj> will show the data key of the object.
    """
    key = "@datainfo"
    locks = "perm(Builders)"
    help_cateogory = "Building"

    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        if not self.args:
            string = "Usage: @datainfo <obj>[=<key>]"
            caller.msg(string)
            return

        # parse agrs
        if not self.rhs:
            if self.args == self.lhs:
                # no "="
                obj_name = self.args
                obj = caller.search(obj_name, location=caller.location)
                if not obj:
                    caller.msg("Sorry, can not find %s." % obj_name)
                else:
                    model = obj.attributes.get(key="model", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)
                    key = obj.attributes.get(key="key", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)

                    if model or key:
                        caller.msg("%s's datainfo is %s" % (obj_name, model + "." + key))
                    else:
                        caller.msg("%s has no datainfo." % obj_name)
                return

        obj_name = self.lhs
        obj = caller.search(obj_name, location=caller.location)
        if not obj:
            caller.msg("Sorry, can not find %s." % obj_name)
            return

        # set the key:
        key_name = self.rhs

        try:
            obj.set_data_info(key_name)
            caller.msg("%s's datainfo has been set to %s" % (obj_name, self.rhs))
        except Exception, e:
            caller.msg("Can't set datainfo %s to %s: %s" % (self.rhs, obj_name, e))


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
            logger.log_errmsg(ostring)
            logger.log_errmsg(traceback.format_exc())
