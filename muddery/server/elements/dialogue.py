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
from muddery.server.utils.utils import async_gather


class MudderyDialogue(BaseElement):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_type = "DIALOGUE"
    element_name = "Dialogue"

    async def load_data(self, key, level=None):
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

    async def match_condition(self, caller, npc):
        """
        Check the dialogue's condition.

        :param caller:
        :param npc:
        :return:
        """
        return await STATEMENT_HANDLER.match_condition(self.condition, caller, npc)

    async def match_dependencies(self, caller):
        """
        Check the dialogue's dependencies.

        :param caller:
        :param npc:
        :return:
        """
        statuses = [QUEST_STATUS_SET.get(dep["type"]) for dep in self.dependencies]
        quests = [dep["quest"] for dep in self.dependencies]
        awaits = [status.match(caller, quest) for status, quest in zip(statuses, quests)]
        if awaits:
            matches = await async_gather(awaits)

            # If there is a False in matches, it will return False, else return True.
            return min(matches)
        else:
            return True

    async def can_finish_quest(self, caller):
        """
        Check whether the dialogue can finish quests to the caller.

        :param caller: the dialogue's caller
        :return:
        """
        if self.finish_quest:
            can_finish = await async_gather([caller.quest_handler.is_accomplished(key) for key in self.finish_quest])

            # If there is a True in can_finish, it will return True, else return False.
            return max(can_finish)
        else:
            return False

    async def can_provide_quest(self, caller):
        """
        Check whether the dialogue can provide quests to the caller.

        :param caller: the dialogue's caller
        :return:
        """
        if self.provide_quest:
            can_provide = await async_gather([caller.quest_handler.can_provide(key) for key in self.provide_quest])

            # If there is a True in can_finish, it will return True, else return False.
            return max(can_provide)
        else:
            return False

    def get_next_dialogues(self):
        """

        :return:
        """
        return self.nexts
