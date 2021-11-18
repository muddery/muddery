"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

import traceback
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from muddery.server.utils import logger
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.system_data import SystemData
from muddery.server.database.gamedata.character_location import CharacterLocation


def create_character(new_player, nickname, character_key=None,
                     level=1, element_type=None, location_key=None, home_key=None):
    """
    Helper function, creates a character based on a player's name.
    """
    if not character_key:
        character_key = GAME_SETTINGS.get("default_player_character_key")

    if not element_type:
        element_type = settings.PLAYER_CHARACTER_ELEMENT_TYPE

    new_character = ELEMENT(element_type)()

    # set player's account id
    new_character.set_account(new_player)

    # Get a new player character id.
    # TODO: load for update
    char_db_id = SystemData.load("last_player_character_id", 0)
    char_db_id += 1
    SystemData.save("last_player_character_id", char_db_id)
    new_character.set_db_id(char_db_id)

    # set location
    if not location_key:
        location_key = GAME_SETTINGS.get("start_location_key")
        if not location_key:
            location_key = GAME_SETTINGS.get("default_player_home_key")
            if not location_key:
                location_key = ""

    CharacterLocation.save(char_db_id, location_key)

    # Add nickname
    if not nickname:
        nickname = character_key

    # save data
    AccountCharacters.add(new_player.get_id(), char_db_id)
    CharacterInfo.add(char_db_id, nickname, level)

    # set nickname
    new_character.set_nickname(nickname)

    # set character info
    new_character.setup_element(character_key, level=level, first_time=True)

    return new_character

