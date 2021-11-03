
from muddery.server.database import gamedata_models as BaseModels


class system_data(BaseModels.system_data):
    pass


# ------------------------------------------------------------
#
# Object's element key.
#
# ------------------------------------------------------------
class object_keys(BaseModels.object_keys):
    pass


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class object_states(BaseModels.object_states):
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
# player character's quests
#
# ------------------------------------------------------------
class character_quests(BaseModels.character_quests):
    """
    Character's quests.
    """
    pass


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class quest_objectives(BaseModels.quest_objectives):
    """
    Quests' objectives.
    """
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
