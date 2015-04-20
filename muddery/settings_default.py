"""
Master configuration file for Muddery.

NOTE: NO MODIFICATIONS SHOULD BE MADE TO THIS FILE!

All settings changes should be done by copy-pasting the variable and
its value to <gamedir>/conf/settings.py.

Hint: Don't copy&paste over more from this file than you actually want
to change.  Anything you don't copy&paste will thus retain its default
value - which may change as Muddery is developed. This way you can
always be sure of what you have changed and what is default behaviour.

"""

import os

######################################################################
# Muddery base server config
######################################################################

MUDDERY_DIR = os.path.dirname(os.path.abspath(__file__))

######################################################################
# World data features
######################################################################

# attribute's category for data info
WORLD_DATA_INFO_CATEGORY = "data_info"

# data app name
WORLD_DATA_APP = "worlddata"

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = "worlddata/data"

# data file's format, only support csv now.
WORLD_DATA_FILE_TYPE = "csv"

# unique rooms
WORLD_ROOMS = ("world_rooms",)

# unique exits
WORLD_EXITS = ("world_exits",)

# unique objects
WORLD_OBJECTS = ("world_objects",)

# details
WORLD_DETAILS = ("world_details",)

# normal objects
PERSONAL_OBJECTS = ("personal_objects",)

# all data models
WORLD_DATA_MODELS = (WORLD_ROOMS,
                     WORLD_EXITS,
                     WORLD_OBJECTS,
                     WORLD_DETAILS,
                     PERSONAL_OBJECTS)

BASE_AUTOOBJ_TYPECLASS = "worldloader.objects.AutoObj"
