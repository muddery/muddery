"""
Set the game's configuration.
"""

from muddery.server.dao.game_settings import GameSettings as GameSettingsData


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
            record_values = GameSettingsData.all()

            if len(record_values) > 0:
                record = record_values[0]
                # Add db fields to dict.
                for field in GameSettingsData.get_fields():
                    self.values[field] = getattr(record, field)
        except Exception as e:
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


GAME_SETTINGS = GameSettings({
    "game_name": "Muddery",
    "connection_screen": "",
    "solo_mode": False,
    "global_cd": 1.0,
    "auto_cast_skill_cd": 1.5,
    "can_give_up_quests": True,
    "can_close_dialogue": False,
    "auto_resume_dialogues": True,
    "default_home_key": "",
    "start_location_key": "",
    "default_player_home_key": "",
    "default_player_character_key": "",
    "default_staff_character_key": "",
})
