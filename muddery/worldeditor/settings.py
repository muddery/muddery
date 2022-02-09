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
    # Muddery base server config
    ######################################################################

    # This is the name of your server.
    GAME_SERVERNAME = "Muddery"

    MUDDERY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAME_DIR = os.getcwd()

    # Worldedotir's pid file
    WORLD_EDITOR_PID = os.path.join(GAME_DIR, "worldeditor.pid")

    # Place to put log files
    LOG_DIR = os.path.join(GAME_DIR, "worldeditor", "logs")
    LOG_NAME = 'server.log'
    LOG_LEVEL = logging.INFO

    ROOT_LOG = "root.log"
    ACCESS_LOG = "access.log"
    ERROR_LOG = "error.log"

    # Administrator's name and password.
    ADMIN_NAME = "admin"

    ADMIN_PASSWORD = "administrator"

    # World data API's url path.
    WORLD_EDITOR_API_PATH = "/api"

    # http port to open for the worldeditor.
    WORLD_EDITOR_PORT = 8002

    # The secret key of jwt.
    WORLD_EDITOR_SECRET = "SET_YOUR_SECRET_KEY"

    # The webpage's root of the world editor.
    WORLD_EDITOR_WEBROOT = os.path.join(GAME_DIR, "web", "worldeditor")

    # Directories from which static files will be gathered from.
    WEBCLIENT_SOURCE_DIRS = (
        (WORLD_EDITOR_WEBROOT, os.path.join(MUDDERY_DIR, "worldeditor", "webclient")),
    )

    # Media files root dir
    MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

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
    DATABASES = {
        'worldeditor': {
            'MODELS': 'worldeditor.models',
            'ENGINE': 'sqlite3',
            'NAME': os.path.join(GAME_DIR, "server", "worldeditor.db3"),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'DEBUG': False,
        },
        'worlddata': {
            'MODELS': 'worlddata.models',
            'ENGINE': 'sqlite3',
            'NAME': os.path.join(GAME_DIR, "server", "worlddata.db3"),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'DEBUG': False,
        },
    }


    ######################################################################
    # World data features
    ######################################################################
    # data app name
    WORLD_DATA_APP = "worlddata"

    # data app name
    WORLD_EDITOR_APP = "worldeditor"

    ######################################################################
    # Typeclasses and other paths
    ######################################################################

    # Path of base world data forms.
    PATH_DATA_FORMS_BASE = "muddery.worldeditor.forms.default_forms"

    # Path of base request processers.
    PATH_REQUEST_PROCESSERS_BASE = "muddery.worldeditor.controllers"

    """
    ######################################################################
    # Database config
    ######################################################################
    

    
    # Database config syntax:
    # ENGINE - path to the the database backend. Possible choices are:
    #            'django.db.backends.sqlite3', (default)
    #            'django.db.backends.mysql',
    #            'django.db.backends.postgresql_psycopg2' (see Issue 241),
    #            'django.db.backends.oracle' (untested).
    # NAME - database name, or path to the db file for sqlite3
    # USER - db admin (unused in sqlite3)
    # PASSWORD - db admin password (unused in sqlite3)
    # HOST - empty string is localhost (unused in sqlite3)
    # PORT - empty string defaults to localhost (unused in sqlite3)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(GAME_DIR, "server", "muddery.db3"),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': ''
        },
    }
    
    # Database Access Object
    DATABASE_STORAGE_OBJECT = 'muddery.server.database.storage.kv_table.KeyValueTable'
    
    # Database Access Object without cache
    DATABASE_CACHE_OBJECT = 'muddery.server.database.storage.memory_storage.MemoryStorage'
    
    # Object's default runtime table. If a typeclass's own runtime table does
    # not exist, will use this table instead.
    DEFAULT_OBJECT_RUNTIME_TABLE = "object_attributes"
    
    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
    
    
    ######################################################################
    # Django web features
    ######################################################################
    
    # While DEBUG is False, show a regular server error page on the web
    # stuff, email the traceback to the people in the ADMINS tuple
    # below. If True, show a detailed traceback for the web
    # browser to display. Note however that this will leak memory when
    # active, so make sure to turn it off for a production server!
    DEBUG = True
    
    # If using Sites/Pages from the web admin, this value must be set to the
    # database-id of the Site (domain) we want to use with this game's Pages.
    SITE_ID = 1
    
    # Context processors define context variables, generally for the template
    # system to use.
    TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                                   'django.core.context_processors.request',
                                   'django.contrib.auth.context_processors.auth',
                                   'django.core.context_processors.debug',)
    
    # resource's location
    IMAGE_PATH = 'image'
    
    # The master urlconf file that contains all of the sub-branches to the
    # applications. Change this to add your own URLs to the website.
    ROOT_URLCONF = 'worldeditor.urls'
    
    # URL prefix for admin media -- CSS, JavaScript and images. Make sure
    # to use a trailing slash. Django1.4+ will look for admin files under
    # STATIC_URL/admin.
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(GAME_DIR, "web", "static")
    
    # URL that handles the webclient.
    WEBCLIENT_ROOT = os.path.join(GAME_DIR, "web", "static", "webclient")
    
    # URL that handles the worldeditor.
    WORLDEDITOR_ROOT = os.path.join(GAME_DIR, "web", "static", "editor")
    
    # Directories from which static files will be gathered from.
    STATICFILES_DIRS = (
        os.path.join(GAME_DIR, "web", "static_overrides"),
        os.path.join(MUDDERY_DIR, "server", "web", "website", "static"),
        ("editor", os.path.join(GAME_DIR, "worldeditor", "webclient")),
        ("editor", os.path.join(MUDDERY_DIR, "worldeditor", "webclient")),
    )
    
    # We setup the location of the website template as well as the admin site.
    WEBSITE_TEMPLATE = "website"
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(GAME_DIR, "web", "template_overrides", WEBSITE_TEMPLATE),
                os.path.join(GAME_DIR, "web", "template_overrides"),
                os.path.join(MUDDERY_DIR, "server", "web", "website", "templates", WEBSITE_TEMPLATE),
                os.path.join(MUDDERY_DIR, "server", "web", "website", "templates")],
            'APP_DIRS': True,
            'OPTIONS': {
                "context_processors": [
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.media',
                    'django.template.context_processors.debug',
                    "django.contrib.messages.context_processors.messages",
                ],
                # While true, show "pretty" error messages for template syntax errors.
                "debug": DEBUG,
            },
        }
    ]
    
    
    # MiddleWare are semi-transparent extensions to Django's functionality.
    # see http://www.djangoproject.com/documentation/middleware/ for a more detailed
    # explanation.
    MIDDLEWARE = [
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",  # 1.4?
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.admindocs.middleware.XViewMiddleware",
        "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    ]
    
    
    # Absolute path to the directory that holds file uploads from web apps.
    # Example: "/home/media/media.lawrence.com"
    MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")
    
    
    ######################################################################
    # Typeclasses and other paths
    ######################################################################
    
    # Element type for accounts.
    ACCOUNT_ELEMENT_TYPE = "ACCOUNT"
    
    # Element type for general characters, include NPCs, mobs and player characters.
    CHARACTER_ELEMENT_TYPE = "CHARACTER"
    
    # Element type for player characters.
    PLAYER_CHARACTER_ELEMENT_TYPE = "PLAYER_CHARACTER"
    
    # Element type for player characters.
    STAFF_CHARACTER_ELEMENT_TYPE = "STAFF_CHARACTER"
    
    # Element type for rooms.
    ROOM_ELEMENT_TYPE = "ROOM"
    
    # Element type for Exit objects.
    EXIT_ELEMENT_TYPE = "EXIT"
    
    # Typeclass for Scripts (fallback). You usually don't need to change this
    # but create custom variations of scripts on a per-case basis instead.
    SCRIPT_ELEMENT_TYPE = "SCRIPT"
    

    
    # Path of base elements.
    PATH_ELEMENTS_BASE = "muddery.server.elements"
    
    # Path of custom elements.
    PATH_ELEMENTS_CUSTOM = "elements"
    
    # Path of base event actions.
    PATH_EVENT_ACTION_BASE = "muddery.server.events.event_actions"
    
    # Path of base quest status.
    PATH_QUEST_STATUS_BASE = "muddery.server.quests.quest_status"
    
    
    ######################################################################
    # Default statement sets
    ######################################################################
    
    # Action functions set
    ACTION_FUNC_SET = "muddery.server.statements.default_statement_func_set.ActionFuncSet"
    
    # Condition functions set
    CONDITION_FUNC_SET = "muddery.server.statements.default_statement_func_set.ConditionFuncSet"
    
    # Skill functions set
    SKILL_FUNC_SET = "muddery.server.statements.default_statement_func_set.SkillFuncSet"
    
    
    ######################################################################
    # Default command sets
    ######################################################################
    # Command set used on the logged-in session
    SESSION_CMDSET = "muddery.server.commands.default_cmdsets.SessionCmdSet"
    
    # Command set for accounts without a character (ooc)
    ACCOUNT_CMDSET = "muddery.server.commands.default_cmdsets.AccountCmdSet"
    
    # Default set for logged in player with characters (fallback)
    CHARACTER_CMDSET = "muddery.server.commands.default_cmdsets.CharacterCmdSet"
    
    
    ######################################################################
    # Muddery additional data features
    ######################################################################
    
    # add data app
    INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.admin",
        "django.contrib.admindocs",
        "django.contrib.flatpages",
        "django.contrib.sites",
        "django.contrib.staticfiles",
        "django.contrib.messages",
        "worlddata",
    ]
    
    # world data model's filename
    WORLD_DATA_MODEL_FILE = "worlddata.models"
    
    ######################################################################
    # Django extensions
    ######################################################################
    
    # Django extesions are useful third-party tools that are not
    # always included in the default django distro.
    try:
        import django_extensions  # noqa
        INSTALLED_APPS = INSTALLED_APPS.append("django_extensions")
    except ImportError:
        # Django extensions are not installed in all distros.
        pass
    
    # data file's folder under user's game directory.
    WORLD_DATA_FOLDER = os.path.join("worlddata", "data")
    
    # add data app
    # INSTALLED_APPS = INSTALLED_APPS + [WORLD_EDITOR_APP, ]
    
    # Localized string data's folder.
    LOCALIZED_STRINGS_FOLDER = "languages"
    
    # Localized string model's name
    LOCALIZED_STRINGS_MODEL = "localized_strings"
    
    
    ###################################
    # permissions
    ###################################
    # Characters who have these permission can bypass events.
    PERMISSION_BYPASS_EVENTS = {"builders", "wizards", "immortals"}
    
    # Characters who have these permission can use text commands.
    PERMISSION_COMMANDS = {"playerhelpers", "builders", "wizards", "immortals"}
    
    
    ###################################
    # world editor
    ###################################
    DEFUALT_LIST_TEMPLATE = "common_list.html"
    
    DEFUALT_FORM_TEMPLATE = "common_form.html"
    
    
    ###################################
    # combat settings
    ###################################
    # Handler of the combat
    NORMAL_COMBAT_HANDLER = "muddery.server.combat.combat_runner.normal_combat.NormalCombat"
    
    HONOUR_COMBAT_HANDLER = "muddery.server.combat.combat_runner.honour_combat.HonourCombat"
    
    #HONOUR_COMBAT_HANDLER = "muddery.server.combat.honour_auto_combat_handler.HonourAutoCombatHandler"
    
    AUTO_COMBAT_TIMEOUT = 60
    
    
    ###################################
    # AI modules
    ###################################
    AI_CHOOSE_SKILL = "muddery.server.ai.choose_skill.ChooseSkill"
    """

SETTINGS = Settings()
