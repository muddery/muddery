
from muddery.server.database import gamedata_models as BaseModels


Base = BaseModels.Base


class system_data(BaseModels.system_data):
    pass


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class character_states(BaseModels.character_states):
    pass


# ------------------------------------------------------------
#
# server bans
#
# ------------------------------------------------------------
class server_bans(BaseModels.server_bans):
    pass


# ------------------------------------------------------------
#
# player's accounts
#
# ------------------------------------------------------------
class accounts(BaseModels.accounts):
    pass


# ------------------------------------------------------------
#
# player account's data
#
# ------------------------------------------------------------
class account_characters(BaseModels.account_characters):
    """
    Character's data.
    """
    pass


# ------------------------------------------------------------
#
# player character's basic information
#
# ------------------------------------------------------------
class character_info(BaseModels.character_info):
    """
    Character's data.
    """
    pass


# ------------------------------------------------------------
#
# player character's revealed maps
#
# ------------------------------------------------------------
class character_revealed_map(BaseModels.character_revealed_map):
    """
    Revealed maps.
    """
    pass


# ------------------------------------------------------------
#
# player character's location
#
# ------------------------------------------------------------
class character_location(BaseModels.character_location):
    """
    Character's location.
    """
    pass


# ------------------------------------------------------------
#
# player character's inventory
#
# ------------------------------------------------------------
class character_inventory(BaseModels.character_inventory):
    """
    Character's inventory.
    """
    pass


# ------------------------------------------------------------
#
# player character's equipments
#
# ------------------------------------------------------------
class character_equipments(BaseModels.character_equipments):
    """
    Character's inventory.
    """
    pass


# ------------------------------------------------------------
#
# player character's skills
#
# ------------------------------------------------------------
class character_skills(BaseModels.character_skills):
    """
    Character's skills.
    """
    pass


# ------------------------------------------------------------
#
# player character's combat
#
# ------------------------------------------------------------
class character_combat(BaseModels.character_combat):
    """
    Character's skills.
    """
    pass


# ------------------------------------------------------------
#
# player character's quests that are doing.
#
# ------------------------------------------------------------
class character_quests(BaseModels.character_quests):
    """
    Character's quests.
    """
    pass


# ------------------------------------------------------------
#
# player character's quests that are finished
#
# ------------------------------------------------------------
class character_finished_quests(BaseModels.character_finished_quests):
    pass


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class character_quest_objectives(BaseModels.character_quest_objectives):
    """
    Quests' objectives.
    """
    pass


# ------------------------------------------------------------
#
# Player character's relationship with other elements.
#
# ------------------------------------------------------------
class character_relationships(BaseModels.character_relationships):
    "Player character's relationship with other elements."
    pass


# ------------------------------------------------------------
#
# closed events
#
# ------------------------------------------------------------
class character_closed_events(BaseModels.character_closed_events):
    pass


# ------------------------------------------------------------
#
# The game's runtime data.
#
# ------------------------------------------------------------
class honours(BaseModels.honours):
    """
    Character's honour data.
    """
    pass
