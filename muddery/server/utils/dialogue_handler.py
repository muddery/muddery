"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from muddery.common.utils import defines
from muddery.server.utils.game_settings import GameSettings
from muddery.server.mappings.element_set import ELEMENT
from muddery.common.utils.singleton import Singleton
from muddery.common.utils.utils import async_gather


class DialogueHandler(Singleton):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize the handler.
        """
        super(DialogueHandler, self).__init__()
        self.dialogue_storage = {}
    
    async def load_cache(self, dlg_key):
        """
        To reduce database accesses, add a cache.

        Args:
            dlg_key (string): dialogue's key
        """
        if not dlg_key:
            return

        if dlg_key in self.dialogue_storage:
            # already cached
            return

        # Add cache of the whole dialogue.
        dlg = ELEMENT("DIALOGUE")()
        await dlg.setup_element(dlg_key)
        self.dialogue_storage[dlg_key] = dlg

    async def get_dialogue(self, dlg_key):
        """
        Get specified dialogue.

        Args:
            dlg_key (string): dialogue's key
        """
        if not dlg_key:
            return

        # Load cache.
        await self.load_cache(dlg_key)

        if dlg_key not in self.dialogue_storage:
            # Can not find dialogue.
            return

        return self.dialogue_storage[dlg_key]

    async def get_npc_dialogues(self, caller, npc):
        """
        Get NPC's dialogues that can show to the caller.

        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            dialogues: (list) a list of available dialogues.
        """
        if not caller:
            return

        if not npc:
            return

        dialogues = []

        # Get npc's dialogues.
        if npc.dialogues:
            dialogues = await async_gather([self.get_dialogue(dlg_key) for dlg_key in npc.dialogues])
            dialogues = [d for d in dialogues if d]
            if dialogues:
                matches = await async_gather([d.match_condition(caller, npc) for d in dialogues])
                dialogues = [d for index, d in enumerate(dialogues) if matches[index]]
                if dialogues:
                    matches = await async_gather([d.match_dependencies(caller) for d in dialogues])
                    dialogues = [d for index, d in enumerate(dialogues) if matches[index]]

        if not dialogues and npc.default_dialogues:
            # Use default sentences.
            # Default sentences should not have condition and dependencies.
            dialogues = await async_gather([self.get_dialogue(dlg_key) for dlg_key in npc.default_dialogues])
            dialogues = [d for d in dialogues if d]

        dialogues = [{"key": d.get_element_key(), "content": d.get_content()} for d in dialogues]

        return {
            "target": {
                "id": npc.get_id(),
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            },
            "dialogues": dialogues,
        }

    async def get_dialogues_by_key(self, dlg_key):
        """
        Get a dialogue by its key.

        Args:
            dlg_key: (string) the key of the current dialogue.

        Returns:
            sentences: (list) a list of available sentences.
        """
        # Get current dialogue.
        dialogue = await self.get_dialogue(dlg_key)
        if not dialogue:
            return

        return {
            "dialogues": [{
                "key": dlg_key,
                "content": dialogue.get_content(),
            }],
        }

    async def get_next_dialogues(self, dlg_key, caller, npc):
        """
        Get dialogues next to this dialogue.

        Args:
            dlg_key: (string) the key of the current dialogue.
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            sentences: (list) a list of available sentences.
        """
        # Get current dialogue.
        dlg = await self.get_dialogue(dlg_key)
        if not dlg:
            return

        target = {}
        if npc:
            target = {
                "id": npc.get_id(),
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            }

        dialogues = []
        dialogues_keys = dlg.get_next_dialogues()
        if dialogues_keys:
            dialogues = await async_gather([self.get_dialogue(dlg_key) for dlg_key in dialogues_keys])
            dialogues = [d for d in dialogues if d]
            if dialogues:
                matches = await async_gather([d.match_condition(caller, npc) for d in dialogues])
                dialogues = [d for index, d in enumerate(dialogues) if matches[index]]
                if dialogues:
                    matches = await async_gather([d.match_dependencies(caller) for d in dialogues if d])
                    dialogues = [d for index, d in enumerate(dialogues) if matches[index]]

        dialogues = [{"key": d.get_element_key(), "content": d.get_content()} for d in dialogues]

        return {
            "target": target,
            "dialogues": dialogues,
        }

    async def get_dialogue_speaker_name(self, caller, npc, speaker_model):
        """
        Get the speaker's text.
        'p' means player.
        'n' means NPC.
        Use string in quotes directly.
        """
        caller_name = ""
        npc_name = ""

        if caller:
            caller_name = caller.get_name()
        if npc:
            npc_name = npc.get_name()

        values = {"p": caller_name,
                  "n": npc_name}
        speaker = speaker_model % values

        return speaker

    def get_dialogue_speaker_icon(self, icon_str, caller, npc, speaker_model):
        """
        Get the speaker's text.
        'p' means player.
        'n' means NPC.
        Use string in quotes directly.
        """
        icon = None

        # use icon resource in dialogue sentence
        if icon_str:
            icon = icon_str
        else:
            if "%(n)" in speaker_model:
                if npc:
                    icon = getattr(npc, "icon", None)
            elif "%(p)" in speaker_model:
                icon = getattr(caller, "icon", None)

        return icon

    async def finish_dialogue(self, dlg_key, caller, npc):
        """
        A dialogue finished, do it's action.
        args:
            dlg_key (string): dialogue's key
            caller (object): the dialogue caller
            npc (object, optional): the dialogue's NPC, can be None
        """
        results = {}

        if not caller:
            return results

        dlg = await self.get_dialogue(dlg_key)
        if not dlg:
            return results

        # do dialogue's event
        events = await caller.event.at_dialogue(dlg_key)
        if events:
            results["events"] = events

        quests = await caller.quest_handler.at_objective(defines.OBJECTIVE_TALK, dlg_key)
        if quests:
            results["quests"] = quests

        return results

    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}
