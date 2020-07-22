"""
All available event actions.
"""

from muddery.server.utils import defines
from muddery.server.utils.localized_strings_handler import _


class QuestObjectiveSet(object):
    """
    All available quest objectives.
    """
    def __init__(self):
        # finish a dialogue, object: dialogue_id
        self.dict = {
            defines.OBJECTIVE_TALK: {
                "name": _("Talk to someone. (The object is the NPC's key.)", category="quest_objective")
            },
            # arrive a room, object: room_id
            defines.OBJECTIVE_ARRIVE: {
                "name": _("Arrive a room. (The object is the room's key.)", category="quest_objective")
            },
            # get some objects, object: object_id
            defines.OBJECTIVE_OBJECT: {
                "name": _("Get some objects. (The object is the object's key.)", category="quest_objective")
            },
            # kill some characters, object: character_id
            defines.OBJECTIVE_KILL: {
                "name": _("Kill someone. (The object is the NPC's key.)", category="quest_objective")
            },
        }

    def all(self):
        """
        Add all forms from the form path.
        """
        return self.dict.keys()

    def choice_all(self):
        """
        Get all event types and names for form choice.
        """
        return [(key, "%s (%s)" % (value["name"], key)) for key, value in self.dict.items()]


QUEST_OBJECTIVE_SET = QuestObjectiveSet()

