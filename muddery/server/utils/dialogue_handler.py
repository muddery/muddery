"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from muddery.server.utils import defines
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.database.dao.dialogues import Dialogues
from muddery.server.database.dao.dialogue_relations import DialogueRelations
from muddery.server.database.dao.dialogue_quests import DialogueQuests
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.events.event_trigger import EventTrigger


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
    
    def load_cache(self, dialogue):
        """
        To reduce database accesses, add a cache.

        Args:
            dialogue (string): dialogue's key
        """
        if not dialogue:
            return

        if dialogue in self.dialogue_storage:
            # already cached
            return

        # Add cache of the whole dialogue.
        self.dialogue_storage[dialogue] = {}
        
        # Get db model
        try:
            dialogue_record = Dialogues.get(dialogue)
            dialogue_record = dialogue_record[0]
        except Exception as e:
            return

        nexts = DialogueRelations.get(dialogue)
        dependencies = DialogueQuests.get(dialogue)

        # Add db fields to data object.
        data = {
            "content": dialogue_record.content,
            "condition": dialogue_record.condition,
        }

        data["dependencies"] = []
        for dependency in dependencies:
            data["dependencies"].append({"quest": dependency.dependency,
                                         "type": dependency.type})

        # get events and quests
        event_trigger = EventTrigger(None, dialogue)

        events = event_trigger.get_events()
        if not events:
            data["event"] = None
            data["provide_quest"] = []
            data["finish_quest"] = []
        else:
            data["event"] = event_trigger
            provide_quest = []
            finish_quest = []
            if defines.EVENT_TRIGGER_DIALOGUE in events:
                for event_info in events[defines.EVENT_TRIGGER_DIALOGUE]:
                    if event_info["action"] == "ACTION_ACCEPT_QUEST":
                        action = EVENT_ACTION_SET.get(event_info["action"])
                        provide_quest.extend(action.get_quests(event_info["key"]))
                    elif event_info["action"] == "ACTION_TURN_IN_QUEST":
                        action = EVENT_ACTION_SET.get(event_info["action"])
                        finish_quest.extend(action.get_quests(event_info["key"]))

            data["provide_quest"] = provide_quest
            data["finish_quest"] = finish_quest

        data["nexts"] = [next_one.next_dlg for next_one in nexts]

        # Add to cache.
        self.dialogue_storage[dialogue] = data

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
            if not STATEMENT_HANDLER.match_condition(npc_dlg["condition"], caller, npc):
                continue

            # Match dependencies.
            match = True
            for dep in npc_dlg["dependencies"]:
                status = QUEST_STATUS_SET.get(dep["type"])
                if not status.match(caller, dep["quest"]):
                    match = False
                    break

            if not match:
                continue

            dialogues.append({
                "key": dlg_key,
                "content": npc_dlg["content"],
            })

        if not dialogues:
            # Use default sentences.
            # Default sentences should not have condition and dependencies.
            for dlg_key in npc.default_dialogues:
                npc_dlg = self.get_dialogue(dlg_key)
                if npc_dlg:
                    dialogues.append({
                        "key": dlg_key,
                        "content": npc_dlg["content"],
                    })
            
        return {
            "target": {
                "dbref": npc.dbref,
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            },
            "dialogues": dialogues,
        }

    def get_dialogues_by_key(self, dlg_key, npc):
        """
        Get a dialogue by its key.

        Args:
            dlg_key: (string) the key of the currrent dialogue.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            sentences: (list) a list of available sentences.
        """
        target = {}
        if npc:
            target = {
                "dbref": npc.dbref,
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
                "content": dialogue["content"],
            }],
        }

    def get_next_dialogues(self, dlg_key, caller, npc):
        """
        Get dialogues next to this dialogue.

        Args:
            dlg_key: (string) the key of the currrent dialogue.
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
                "dbref": npc.dbref,
                "name": npc.get_name(),
                "icon": getattr(npc, "icon", None),
            }

        dialogues = []
        for next_dlg_key in dlg["nexts"]:
            # Get next dialogue.
            next_dlg = self.get_dialogue(next_dlg_key)
            if not next_dlg:
                continue

            # Match conditions.
            if not STATEMENT_HANDLER.match_condition(next_dlg["condition"], caller, npc):
                continue

            # Match dependencies.
            match = True
            for dep in next_dlg["dependencies"]:
                status = QUEST_STATUS_SET.get(dep["type"])
                if not status.match(caller, dep["quest"]):
                    match = False
                    break

            if not match:
                continue

            dialogues.append({
                "key": next_dlg_key,
                "content": next_dlg["content"],
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
        if dlg["event"]:
            dlg["event"].at_dialogue(caller, npc)

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

            if finish_quest:
                break

            if not caller.quest_handler.get_accomplished_quests():
                if provide_quest:
                    break

        return provide_quest, finish_quest

    def dialogue_have_quest(self, caller, npc, dialogue):
        """
        Find quests by recursion.
        """
        provide_quest = False
        finish_quest = False

        # check if the dialogue is available
        npc_dlg = self.get_dialogue(dialogue)
        if not npc_dlg:
            return provide_quest, finish_quest

        if not STATEMENT_HANDLER.match_condition(npc_dlg["condition"], caller, npc):
            return provide_quest, finish_quest

        match = True
        for dep in npc_dlg["dependencies"]:
            status = QUEST_STATUS_SET.get(dep["type"])
            if not status.match(caller, dep["quest"]):
                match = False
                break
        if not match:
            return provide_quest, finish_quest

        # find quests in its sentences
        for quest_key in npc_dlg["finish_quest"]:
            if caller.quest_handler.is_accomplished(quest_key):
                finish_quest = True
                return provide_quest, finish_quest

        if not provide_quest and npc_dlg["provide_quest"]:
            for quest_key in npc_dlg["provide_quest"]:
                if caller.quest_handler.can_provide(quest_key):
                    provide_quest = True
                    return provide_quest, finish_quest

        for dlg_key in npc_dlg["nexts"]:
            # get next dialogue
            provide, finish = self.dialogue_have_quest(caller, npc, dlg_key)
                
            provide_quest = (provide_quest or provide)
            finish_quest = (finish_quest or finish)

            if finish_quest:
                break

            if not caller.quest_handler.get_accomplished_quests():
                if provide_quest:
                    break

        return provide_quest, finish_quest


# main dialogue handler
DIALOGUE_HANDLER = DialogueHandler()
