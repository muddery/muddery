"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.database.worlddata.dialogues import Dialogues
from muddery.server.database.worlddata.dialogue_relations import DialogueRelations
from muddery.server.database.worlddata.dialogue_quests import DialogueQuests
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET


class MudderyDialogue(BaseElement):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_type = "DIALOGUE"
    element_name = "Dialogue"

    def load_data(self, key, level=None):
        """
        Load the object's data.

        :arg
            key: (string) the key of the data.
            level: (int) element's level.

        :return:
        """
        # Load data.
        # Get db model
        try:
            dialogue_record = Dialogues.get(key)
            dialogue_record = dialogue_record[0]
        except Exception as e:
            return

        # Add db fields to data object.
        self.content = dialogue_record.content
        self.condition = dialogue_record.condition

        dependencies = DialogueQuests.get(key)
        self.dependencies = [{
            "quest": d.dependency,
            "type": d.type
        } for d in dependencies]

        self.event = None
        self.provide_quest = []
        self.finish_quest = []

        nexts = DialogueRelations.get(key)
        self.nexts = [next_one.next_dlg for next_one in nexts]

    def get_content(self):
        """
        Get the dialogue's content.
        :return:
        """
        return self.content

    def match_condition(self, caller, npc):
        """
        Check the dialogue's condition.

        :param caller:
        :param npc:
        :return:
        """
        return STATEMENT_HANDLER.match_condition(self.condition, caller, npc)

    def match_dependencies(self, caller):
        """
        Check the dialogue's dependencies.

        :param caller:
        :param npc:
        :return:
        """
        for dep in self.dependencies:
            status = QUEST_STATUS_SET.get(dep["type"])
            if not status.match(caller, dep["quest"]):
                return False

        return True

    def can_finish_quest(self, caller):
        """
        Check whether the dialogue can finish quests to the caller.

        :param caller: the dialogue's caller
        :return:
        """
        for quest_key in self.finish_quest:
            if caller.quest_handler.is_accomplished(quest_key):
                return True

        return False

    def can_provide_quest(self, caller):
        """
        Check whether the dialogue can provide quests to the caller.

        :param caller: the dialogue's caller
        :return:
        """
        for quest_key in self.provide_quest:
            if caller.quest_handler.can_provide(quest_key):
                return True

        return False

    def get_next_dialogues(self):
        """

        :return:
        """
        return self.nexts
