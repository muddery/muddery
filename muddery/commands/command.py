"""
Commands

Add three commands: @importcsv, @datainfo and @batchbuilder

"""

import os
import re
from django.conf import settings
from django.db.models.loading import get_model
from muddery.utils.importer import import_csv, import_csv_all
from muddery.utils.loader import set_obj_data_info
from muddery.utils.builder import build_all
from evennia import default_cmds


#------------------------------------------------------------
# import csv tables
#------------------------------------------------------------
class CmdImportCsv(default_cmds.MuxCommand):
    """
    Usage:
      @importcsv

      If <modelname> is empty, it will import all csv files in settings.WORLD_DATA_MODELS.
    """
    key = "@importcsv"
    locks = "perm(Builders)"
    help_cateogory = "Builders"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"

        caller = self.caller
        
        # count the number of files loaded
        count = 0
        
        # get app_name
        app_name = settings.WORLD_DATA_APP
        
        # get model_name, can specify the model name in args
        # if no args is given, load all models in settings.WORLD_DATA_MODELS
        models = self.args
        if models:
            models = [arg.strip() for arg in models.split(',')]
        else:
            models = [model for data_models in settings.WORLD_DATA_MODELS
                            for model in data_models]

        # import models one by one
        for model_name in models:

            # make file name
            file_name = os.path.join(settings.GAME_DIR, settings.CSV_DATA_FOLDER, model_name + ".csv")
            
            # import data
            try:
                import_csv(file_name, app_name, model_name)
                caller.msg("%s imported." % model_name)
                count += 1
            except Exception, e:
                print e
                continue

        caller.msg("total %d files imported." % count)


#------------------------------------------------------------
# set object's info_db and info_key
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
        
        if not self.rhs:
            if self.args == self.lhs:
                # no "="
                obj_name = self.args
                obj = caller.search(obj_name, location=caller.location)
                if not obj:
                    caller.msg("Sorry, can not find %s." % obj_name)
                elif obj.db.info_db and obj.db.info_key:
                    caller.msg("%s's datainfo is %s" % (obj_name, obj.db.info_db + "." + obj.db.info_key))
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
        model_name = ""
        
        if key_name:
            models = [model for data_models in settings.WORLD_DATA_MODELS
                            for model in data_models]
                    
            for model in models:
                model_obj = get_model(settings.WORLD_DATA_APP, model)
                if model_obj:
                    if model_obj.objects.filter(key=key_name):
                        model_name = model
                        app_name = settings.WORLD_DATA_APP
                        break

        try:
            set_obj_data_info(obj, model_name, key_name)
            caller.msg("%s's datainfo has been set to %s" % (obj_name, self.rhs))
        except Exception, e:
            caller.msg("Can't set datainfo %s to %s: %s" % (self.rhs, obj_name, e))


#------------------------------------------------------------
# batch builder
#------------------------------------------------------------
class CmdBatchBuilder(default_cmds.MuxCommand):
    """
    Usage:
      @batchbuilder
      
    Build the whole game world with data in CSV files.
    """
    key = "@batchbuilder"
    aliases = ["@batchbld"]
    locks = "perm(Builders)"
    help_cateogory = "Builders"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"
        import_csv_all(self.caller)
        build_all(self.caller)

