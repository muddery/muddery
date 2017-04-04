"""
Set the game's configuration.
"""


from muddery.worlddata.data_sets import DATA_SETS
from evennia.utils import logger


class GameSettings(object):
    """
    Handles a character's custom attributes.
    """
    def __init__(self, model, default_values):
        """
        Initialize handler.
        """
        self.values = {}
        self.default_values = default_values
        self.model = model
        self.reset()

    def reset(self):
        """
        Reset values.
        """

        # set default values
        self.values = self.default_values

        # Get db model
        try:
            query = self.model.objects.all()
            if len(query) > 0:
                record = query[0]
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


GAME_SETTINGS = GameSettings(DATA_SETS.game_settings.model,
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


CLIENT_SETTINGS = GameSettings(DATA_SETS.client_settings.model,
                               {"game_title": "",
                                "map_room_size": 40,
                                "map_scale": 75,
                                "show_command_box": False,
                                "can_close_dialogue": False,
                                })
