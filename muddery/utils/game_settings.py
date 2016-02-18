"""
AttributeHandler handles a character's custom attributes.
"""


from django.conf import settings
from django.apps import apps
from evennia.utils import logger


class GameSettings(object):
    """
    Handles a character's custom attributes.
    """
    def __init__(self):
        """
        Initialize handler.
        """
        self.data = {}
        self.reset()

    def reset(self):
        """
        Reset values.
        """

        # set default values
        self.data = {"connection_screen": "",
                     "solo_mode": False,
                     "global_cd": 1.0,
                     "auto_cast_skill_cd": 1.5,
                     "player_reborn_cd": 10.0,
                     "npc_reborn_cd": 10.0,
                     "allow_give_up_quests": True,
                     "default_home_key": True,
                     "start_location_key": True,
                     "default_player_home_key": True,
                     "default_player_model_key": ""}

        # Get db model
        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, settings.GAME_SETTINGS)
            if len(model_obj.objects.all()) > 0:
                record = model_obj.objects.all()[0]
                # Add db fields to dict.
                for field in record._meta.fields:
                    self.data[field.name] = record.serializable_value(field.name)
        except Exception, e:
            print("Can not load settings: %s" % e)
            pass


    def get(self, key):
        """
        Get an attribute. If the key does not exist, returns default.
        """
        if not key in self.data:
            raise AttributeError

        return self.data[key]


    def set(self, key, value):
        """
        Set an attribute.
        """
        self.data[key] = value


GAME_SETTINGS = GameSettings()
