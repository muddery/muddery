"""
Set the game's configuration.
"""


from django.conf import settings
from django.apps import apps
from muddery.worlddata.data_handler import DATA_HANDLER
from evennia.utils import logger


class GameSettings(object):
    """
    Handles a character's custom attributes.
    """
    def __init__(self, model_name, default_values):
        """
        Initialize handler.
        """
        self.values = {}
        self.default_values = default_values
        self.model_name = model_name
        self.reset()


    def reset(self):
        """
        Reset values.
        """

        # set default values
        self.values = self.default_values

        # Get db model
        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
            if len(model_obj.objects.all()) > 0:
                record = model_obj.objects.all()[0]
                # Add db fields to dict.
                for field in record._meta.fields:
                    self.values[field.name] = record.serializable_value(field.name)
        except Exception, e:
            print("Can not load settings: %s" % e)
            pass


    def get(self, key):
        """
        Get an attribute. If the key does not exist, returns default.
        """
        if not key in self.values:
            raise AttributeError

        return self.values[key]


    def set(self, key, value):
        """
        Set an attribute.
        """
        self.values[key] = value


    def all_values(self):
        """
        Get all settings.

        Returns:
            values: (map) all values
        """
        return self.values


GAME_SETTINGS = GameSettings(DATA_HANDLER.OtherData.GAME_SETTINGS,
                             {"connection_screen": "",
                              "solo_mode": False,
                              "global_cd": 1.0,
                              "auto_cast_skill_cd": 1.5,
                              "player_reborn_cd": 10.0,
                              "npc_reborn_cd": 10.0,
                              "can_give_up_quests": True,
                              "single_dialogue_sentence": False,
                              "auto_resume_dialogues": True,
                              "default_home_key": True,
                              "start_location_key": True,
                              "default_player_home_key": True,
                              "default_player_character_key": "",
                              })


CLIENT_SETTINGS = GameSettings(DATA_HANDLER.OtherData.CLIENT_SETTINGS,
                               {"game_title": "",
                                "map_room_size": 40,
                                "map_scale": 75,
                                "show_command_box": False,
                                "can_close_dialogue": False,
                                })
