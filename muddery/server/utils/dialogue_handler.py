"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from muddery.server.utils import defines
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.mappings.element_set import ELEMENT


class DialogueHandler(object):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize the handler.
        """
        self.can_close_dialogue = GAME_SETTINGS.get("can_close_dialogue")
        self.dialogue_storage = {}
    
    def load_cache(self, dlg_key):
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
        dlg.setup_element(dlg_key)
        self.dialogue_storage[dlg_key] = dlg


    def get_dialogue(self, dlg_key):
        """
        Get specified dialogue.

        Args:
            dlg_key (string): dialogue's key
        """
        if not dlg_key:
            return

        # Load cache.
        self.load_cache(dlg_key)

        if dlg_key not in self.dialogue_storage:
            # Can not find dialogue.
            return

        return self.dialogue_storage[dlg_key]

    def get_npc_dialogues(self, caller, npc):
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
        for dlg_key in npc.dialogues:
            # Get all dialogues.
            npc_dlg = self.get_dialogue(dlg_key)
            if not npc_dlg:
                continue

            # Match conditions.
            if not npc_dlg.match_condition(caller, npc):
                continue

            # Match dependencies.
            if not npc_dlg.match_dependencies(caller):
                continue

            dialogues.append({
                "key": dlg_key,
                "content": npc_dlg.get_content(),
            })

        if not dialogues:
            # Use default sentences.
            # Default sentences should not have condition and dependencies.
            for dlg_key in npc.default_dialogues:
                npc_dlg = self.get_dialogue(dlg_key)
                if npc_dlg:
                    dialogues.append({
                        "key": dlg_key,
                        "content": npc_dlg.get_content(),
                    })
            
        return {
            "target": {
                "id": npc.get_id(),
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            },
            "dialogues": dialogues,
        }

    def get_dialogues_by_key(self, dlg_key, npc):
        """
        Get a dialogue by its key.

        Args:
            dlg_key: (string) the key of the current dialogue.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            sentences: (list) a list of available sentences.
        """
        target = {}
        if npc:
            target = {
                "id": npc.get_id(),
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            }

        # Get current dialogue.
        dialogue = self.get_dialogue(dlg_key)
        if not dialogue:
            return

        return {
            "target": target,
            "dialogues": [{
                "key": dlg_key,
                "content": dialogue.get_content(),
            }],
        }

    def get_next_dialogues(self, dlg_key, caller, npc):
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
        dlg = self.get_dialogue(dlg_key)
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
        for next_dlg_key in dlg.get_next_dialogues():
            # Get next dialogue.
            next_dlg = self.get_dialogue(next_dlg_key)
            if not next_dlg:
                continue

            # Match conditions.
            if not next_dlg.match_condition(caller, npc):
                continue

            # Match dependencies.
            if not next_dlg.match_dependencies(caller):
                continue

            dialogues.append({
                "key": next_dlg_key,
                "content": next_dlg.get_content(),
            })

        return {
            "target": target,
            "dialogues": dialogues,
        }

    def get_dialogue_speaker_name(self, caller, npc, speaker_model):
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

    def finish_dialogue(self, dlg_key, caller, npc):
        """
        A dialogue finished, do it's action.
        args:
            dlg_key (string): dialogue's key
            caller (object): the dialogue caller
            npc (object, optional): the dialogue's NPC, can be None
        """
        if not caller:
            return

        dlg = self.get_dialogue(dlg_key)
        if not dlg:
            return

        # do dialogue's event
        caller.event.at_dialogue(dlg_key)

        caller.quest_handler.at_objective(defines.OBJECTIVE_TALK, dlg_key)

    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}

    def have_quest(self, caller, npc):
        """
        Check if the npc can provide or finish quests.
        Completing is higher than providing.
        """
        provide_quest = False
        finish_quest = False

        if not caller:
            return provide_quest, finish_quest

        if not npc:
            return provide_quest, finish_quest

        # get npc's default dialogues
        for dlg_key in npc.dialogues:
            # find quests by recursion
            provide, finish = self.dialogue_have_quest(caller, npc, dlg_key)
                
            provide_quest = (provide_quest or provide)
            finish_quest = (finish_quest or finish)

            if finish_quest or provide_quest:
                break

        return provide_quest, finish_quest

    def dialogue_have_quest(self, caller, npc, dlg_key):
        """
        Find quests by recursion.
        """
        provide_quest = False
        finish_quest = False

        # check if the dialogue is available
        npc_dlg = self.get_dialogue(dlg_key)
        if not npc_dlg:
            return provide_quest, finish_quest

        if not npc_dlg.match_condition(caller, npc):
            return provide_quest, finish_quest

        if not npc_dlg.match_dependencies(caller):
            return provide_quest, finish_quest

        # find quests in its sentences
        if npc_dlg.can_finish_quest(caller):
            finish_quest = True
            return provide_quest, finish_quest

        if npc_dlg.can_provide_quest(caller):
            provide_quest = True
            return provide_quest, finish_quest

        for dlg_key in npc_dlg.get_next_dialogues():
            # get next dialogue
            provide, finish = self.dialogue_have_quest(caller, npc, dlg_key)
                
            provide_quest = (provide_quest or provide)
            finish_quest = (finish_quest or finish)

            if finish_quest or provide_quest:
                break

        return provide_quest, finish_quest


# main dialogue handler
DIALOGUE_HANDLER = DialogueHandler()
