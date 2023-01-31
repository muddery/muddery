"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from muddery.common.utils import defines
from muddery.common.utils.utils import async_wait, async_gather
from muddery.server.utils.logger import logger
from muddery.server.database.worlddata.dialogues import Dialogues
from muddery.server.database.worlddata.dialogue_relations import DialogueRelations
from muddery.server.elements.base_element import BaseElement
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.mappings.dialogue_set import DialogueSet


class MudderyDialogue(BaseElement):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_type = "DIALOGUE"
    element_name = "Dialogue"

    def __init__(self, *agrs, **wargs):
        """
        Initial the object.
        """
        super(MudderyDialogue, self).__init__(*agrs, **wargs)

        self.content = ""
        self.event = None
        self.provide_quest = []
        self.finish_quest = []
        self.nexts = []

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
            logger.log_err("Can not load dialogue: %s" % key)
            return

        # Add db fields to data object.
        self.content = dialogue_record.content

        records = DialogueRelations.get(key)
        self.nexts = [{
            "key": record.next_dlg,
            "condition": record.condition,
            "otherwise": record.otherwise,
        } for record in records]

        if self.nexts:
            # load dialogues to the cache
            await async_wait([DialogueSet.inst().load_dialogue(item["key"]) for item in self.nexts])

    def get_content(self):
        """
        Get the dialogue's content.
        :return:
        """
        return self.content

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

    async def get_next_dialogues(self, caller, npc):
        """
        Get dialogues next to this dialogue.

        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            sentences: (list) a list of available sentences.
        """
        if not self.nexts:
            return

        target = {}
        if npc:
            target = {
                "id": npc.get_id(),
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            }

        dialogues = []

        if self.nexts:
            candidates = [item for item in self.nexts if not item["otherwise"]]
            if candidates:
                matches = await async_gather([STATEMENT_HANDLER.match_condition(item["condition"], caller, npc)
                                              for item in candidates])
                dialogues = [DialogueSet.inst().get_dialogue(item["key"]) for index, item in enumerate(candidates)
                             if matches[index]]

            if not dialogues:
                # Get otherwise sentences.
                dialogues = [DialogueSet.inst().get_dialogue(item["key"]) for item in self.nexts if item["otherwise"]]

        dialogues = [{"key": d.get_element_key(), "content": d.get_content()} for d in dialogues]

        return {
            "target": target,
            "dialogues": dialogues,
        }

    async def finish_dialogue(self, caller, npc):
        """
        A dialogue finished, do its action.
        args:
            caller (object): the dialogue caller
            npc (object, optional): the dialogue's NPC, can be None
        """
        results = {}

        if not caller:
            return results

        # do dialogue's event
        events = await caller.event.at_dialogue(self.get_element_key())
        if events:
            results["events"] = events

        quests = await caller.quest_handler.at_objective(defines.OBJECTIVE_TALK, self.get_element_key())
        if quests:
            results["quests"] = quests

        return results
