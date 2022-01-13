"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

import traceback
from muddery.server.conf import settings
from muddery.server.utils.logger import logger
from muddery.server.utils.game_settings import GameSettings
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.database.gamedata.account_characters import AccountCharacters
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.system_data import SystemData
from muddery.server.database.gamedata.character_location import CharacterLocation


async def create_character(new_player, nickname, character_key=None,
                     level=1, element_type=None, location_key=None, home_key=None):
    """
    Helper function, creates a character based on a player's name.
    """
    if not character_key:
        character_key = GameSettings.inst().get("default_player_character_key")

    if not element_type:
        element_type = settings.PLAYER_CHARACTER_ELEMENT_TYPE

    new_character = ELEMENT(element_type)()

    # set player's account id
    new_character.set_account(new_player)

    # Get a new player character id.
    char_db_id = await SystemData.inst().load("last_player_character_id", 0, for_update=True)
    char_db_id += 1
    await SystemData.inst().save("last_player_character_id", char_db_id)
    new_character.set_db_id(char_db_id)

    # set location
    if not location_key:
        location_key = GameSettings.inst().get("start_location_key")
        if not location_key:
            location_key = GameSettings.inst().get("default_player_home_key")
            if not location_key:
                location_key = ""

    await CharacterLocation.inst().save(char_db_id, location_key)

    # Add nickname
    if not nickname:
        nickname = character_key

    # save data
    await AccountCharacters.inst().add(new_player.get_id(), char_db_id)
    await CharacterInfo.inst().add(char_db_id, nickname, level)

    # set nickname
    await new_character.set_nickname(nickname)

    # set character info
    await new_character.setup_element(character_key, level=level, first_time=True)

    return new_character
