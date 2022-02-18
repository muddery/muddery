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
import logging


class Settings(object):
    """
    World editor's default settings.
    """

    def update(self, settings):
        """
        Update configs with another Configs object.
        """
        for name in settings.__class__.__dict__:
            if name[0] != "_":
                setattr(self, name, getattr(settings, name))

    ######################################################################
    # Base server settings
    ######################################################################

    # This is the name of your server.
    GAME_SERVERNAME = "Muddery"

    # Administrator's name and password.
    ADMIN_NAME = "admin"

    ADMIN_PASSWORD = "administrator"


    ######################################################################
    # Network settings
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOST = "0.0.0.0"

    # http port to open for the worldeditor.
    WORLD_EDITOR_PORT = 8002

    # The secret key of jwt.
    WORLD_EDITOR_SECRET = "SET_YOUR_SECRET_KEY"


    ######################################################################
    # Folders and files settings
    ######################################################################

    MUDDERY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAME_DIR = os.getcwd()

    # Worldedotir's pid file
    WORLD_EDITOR_PID = os.path.join(GAME_DIR, "worldeditor.pid")


    ######################################################################
    # Logging settings
    ######################################################################
    # Place to put log files
    LOG_NAME = 'muddery_worldeditor'
    LOG_FILE = os.path.join(GAME_DIR, "worldeditor", "logs", "editor.log")
    LOG_LEVEL = logging.WARNING

    # Also print logs to the console.
    LOG_TO_CONSOLE = False

    ROOT_LOG = "root.log"
    ACCESS_LOG = "access.log"
    ERROR_LOG = "error.log"


    ######################################################################
    # Database config
    # ENGINE: Database's engine. Possible choices are:
    #         'sqlite3'
    #         'mysql'
    # NAME - database name, or path to the db file for sqlite3
    # USER - db admin (unused in sqlite3)
    # PASSWORD - db admin password (unused in sqlite3)
    # HOST - empty string is localhost (unused in sqlite3)
    # PORT - empty string defaults to localhost (unused in sqlite3)
    ######################################################################
    WORLDEDITOR_DB = {
        'MODELS': 'worldeditor.models',
        'ENGINE': 'sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "worldeditor.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'DEBUG': False,
    }


    ######################################################################
    # Web features
    ######################################################################

    # World data API's url path.
    WORLD_EDITOR_API_PATH = "/api"

    # World data upload file's path.
    WORLD_EDITOR_UPLOAD_PATH = "/upload"

    # The webpage's root of the world editor.
    WORLD_EDITOR_WEBROOT = os.path.join(GAME_DIR, "web", "worldeditor")

    # Directories from which static files will be gathered from.
    WEBCLIENT_SOURCE_DIRS = (
        (WORLD_EDITOR_WEBROOT, os.path.join(MUDDERY_DIR, "worldeditor", "webclient")),
        (WORLD_EDITOR_WEBROOT, os.path.join(GAME_DIR, "worldeditor", "webclient")),
    )

    # Media files root dir
    MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

    # Encrypt secret messages in transporting messages.
    ENABLE_ENCRYPT = True

    # RSA private key file
    RSA_PRIVATE_KEY_FILE = os.path.join(GAME_DIR, "worldeditor", "keys", "rsa_private.pem")


    ######################################################################
    # Elements and other paths
    ######################################################################

    # Path of base world data forms.
    PATH_DATA_FORMS_BASE = "muddery.worldeditor.forms.default_forms"

    # Path of base request processers.
    PATH_REQUEST_PROCESSERS_BASE = "muddery.worldeditor.controllers"


SETTINGS = Settings()
