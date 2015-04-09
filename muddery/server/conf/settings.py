"""
Evennia settings file.

The full options are found in the default settings file found here:

/Users/kellysmile27/Python/devel/evennia/settings_default.py

Note: Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

"""

# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# Place to put log files
LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
SERVER_LOG_FILE = os.path.join(LOG_DIR, 'server.log')
PORTAL_LOG_FILE = os.path.join(LOG_DIR, 'portal.log')
HTTP_LOG_FILE = os.path.join(LOG_DIR, 'http_requests.log')


######################################################################
# Django web features
######################################################################

# Absolute path to the directory that holds file uploads from web apps.
# Example: "/home/media/media.lawrence.com"
MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

# The master urlconf file that contains all of the sub-branches to the
# applications. Change this to add your own URLs to the website.
ROOT_URLCONF = 'web.urls'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure
# to use a trailing slash. Django1.4+ will look for admin files under
# STATIC_URL/admin.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(GAME_DIR, "web", "static")

# Directories from which static files will be gathered from.
STATICFILES_DIRS = (
    os.path.join(GAME_DIR, "web", "static_overrides"),
    os.path.join(EVENNIA_DIR, "web", "static"),)

# We setup the location of the website template as well as the admin site.
TEMPLATE_DIRS = (
    os.path.join(GAME_DIR, "web", "template_overrides"),
    os.path.join(EVENNIA_DIR, "web", "templates", ACTIVE_TEMPLATE),
    os.path.join(EVENNIA_DIR, "web", "templates"),)


######################################################################
# World data features
######################################################################

# attribute's category for data info
WORLD_DATA_INFO_CATEGORY = "data_info"

# data app name
WORLD_DATA_APP = "worlddata"

# csv files' folder under user's game directory.
CSV_DATA_FOLDER = "worlddata/csv"

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
