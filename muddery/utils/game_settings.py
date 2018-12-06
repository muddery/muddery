"""
Set the game's configuration.
"""

from django.conf import settings
from muddery.worlddata.dao import common_mappers as CM
from evennia.utils import logger


class GameSettings(object):
    """
    Handles a character's custom attributes.
    """
    def __init__(self, default_values):
        """
        Initialize handler.
        """
        self.values = {}
        self.default_values = default_values
        self.reset()

    def reset(self):
        """
        Reset values.
        """

        # set default values
        self.values = self.default_values

        # Get db model
        try:
            record_values = CM.GAME_SETTINGS.all()

            if len(record_values) > 0:
                record = record_values[0]
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

    def get_client_settings(self):
        """
        Get settings for the webclient.

        Returns:
            (dict) settings
        """
        client_settings = {"language": settings.LANGUAGE_CODE,
                           "game_name": self.get("game_name"),
                           "solo_mode": self.get("solo_mode"),
                           "map_scale": self.get("map_scale"),
                           "map_room_size": self.get("map_room_size"),
                           "map_room_box": self.get("map_room_box"),
                           "min_honour_level": settings.MIN_HONOUR_LEVEL,}
        return client_settings


GAME_SETTINGS = GameSettings({"game_name": "Muddery",
                              "connection_screen": "",
                              "solo_mode": False,
                              "global_cd": 1.0,
                              "auto_cast_skill_cd": 1.5,
                              "can_give_up_quests": True,
                              "can_close_dialogue": False,
                              "single_dialogue_sentence": False,
                              "auto_resume_dialogues": True,
                              "default_home_key": True,
                              "start_location_key": True,
                              "default_player_home_key": True,
                              "default_player_character_key": "",
                              "map_scale": 75.0,
                              "map_room_size": 40.0,
                              "map_room_box": False,
                              })
