"""
This module handles importing data from files to models.
"""

import os
import csv
from django.db import models
from django.db.models.loading import get_model
from django.conf import settings
from evennia.utils import logger


def import_csv(file_name, model_name):
    """
    Import data from a csv file to the db model
    
    Args:
        file_name: (string) CSV file's name.
        app_name: (string) Db app's name.
        model_name: (string) Db model's name.
    """
    try:
        # load file
        csvfile = open(file_name, 'r')
        reader = csv.reader(csvfile)
        
        # get app name
        app_name = settings.WORLD_DATA_APP
        
        # get model
        model_obj = get_model(app_name, model_name)
        
        # clear old data
        model_obj.objects.all().delete()
        
        # read title
        title = reader.next()
        
        # get field types
        """
        type = 0    means common field
        type = 1    means ForeignKey field
        type = 2    means ManyToManyField field, not support
        type = -1   means field does not exist
        """
        
        types = []
        related_fields = []
        for field_name in title:
            type = -1
            related_field = 0
            
            try:
                # get field info
                field = model_obj._meta.get_field(field_name)

                if isinstance(field, models.ForeignKey):
                    type = 1
                    related_field = field.related_field
                elif isinstance(field, models.ManyToManyField):
                    type = 2
                else:
                    type = 0
            except Exception, e:
                logger.log_errmsg("Field error: %s" % e)
                pass

            types.append(type)
            related_fields.append(related_field)
        
        # import values
        # read next line
        values = reader.next()
        while values:
            try:
                record = {}
                for item in zip(title, types, values, related_fields):
                    field_name = item[0]
                    type = item[1]
                    value = item[2]
                    related_field = item[3]
                
                    # set field values
                    if type == 0:
                        record[field_name] = value
                    elif type == 1:
                        arg = {}
                        arg[related_field.name] = value
                        record[field_name] = related_field.model.objects.get(**arg)
            
                # create new record
                data = model_obj.objects.create(**record)
                data.save()
            except Exception, e:
                logger.log_errmsg("Can't load data: %s" % e)

            # read next line
            values = reader.next()

    except StopIteration:
        # reach the end of file, pass this exception
        pass


def import_file(file_name, model_name):
    """
    Import data from a data file to the db model
    
    Args:
        file_name: (string) Data file's name.
        model_name: (string) Db model's name.
    """
    
    type = settings.WORLD_DATA_FILE_TYPE.lower()
    ext_name = ""
    if type == "csv":
        ext_name = ".csv"
    else:
        ostring = "Does not support file type %s" % settings.WORLD_DATA_FILE_TYPE
        print ostring
        if caller:
            caller.msg(ostring)
        return

    if type == "csv":
        import_csv(file_name, model_name)


def import_all(caller=None):
    """
    Import all data files to models.
    
    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """

    # count the number of files loaded
    count = 0
    
    # get app name
    app_name = settings.WORLD_DATA_APP

    # get model name
    models = [model for data_models in settings.WORLD_DATA_MODELS
                    for model in data_models]
    
    # get file's extension name
    type = settings.WORLD_DATA_FILE_TYPE.lower()
    ext_name = ""
    if type == "csv":
        ext_name = ".csv"
    else:
        ostring = "Does not support file type %s" % settings.WORLD_DATA_FILE_TYPE
        print ostring
        if caller:
            caller.msg(ostring)
        return
    
    # import models one by one
    for model_name in models:
        # make file name
        file_name = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER, model_name + ext_name)
        
        # import data
        try:
            if type == "csv":
                import_csv(file_name, model_name)

            ostring = "%s imported" % model_name
            print ostring
            if caller:
                caller.msg(ostring)
            
            count += 1
        except Exception, e:
            ostring = "Can not import %s: %s" % (model_name, e)
            print ostring
            if caller:
                caller.msg(ostring)
            continue
    
    ostring = "Total %d files imported.\n" % count
    print ostring
    if caller:
        caller.msg(ostring)
