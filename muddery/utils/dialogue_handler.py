"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""


from muddery.utils import defines
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
from muddery.utils.script_handler import SCRIPT_HANDLER
from muddery.utils import defines
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class DialogueHandler(object):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize the handler.
        """
        self.dialogue_storage = {}
    
    
    def load_cache(self, dialogue):
        """
        To reduce database accesses, add a cache.
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
            model_dialogues = get_model(settings.WORLD_DATA_APP, settings.DIALOGUES)
            dialogue_record = model_dialogues.objects.get(key=dialogue)
        except Exception, e:
            return

        sentences = []
        model_sentences = get_model(settings.WORLD_DATA_APP, settings.DIALOGUE_SENTENCES)
        if model_sentences:
            # Get records.
            sentences = model_sentences.objects.filter(dialogue=dialogue)

        nexts = []
        model_nexts = get_model(settings.WORLD_DATA_APP, settings.DIALOGUE_RELATIONS)
        if model_nexts:
            # Get records.
            nexts = model_nexts.objects.filter(dialogue=dialogue)

        dependencies = []
        model_dependencies = get_model(settings.WORLD_DATA_APP, settings.DIALOGUE_QUEST_DEPENDENCY)
        if model_dependencies:
            # Get records.
            dependencies = model_dependencies.objects.filter(dialogue=dialogue)


        # Add db fields to data object.
        data = {}

        data["condition"] = dialogue_record.condition

        data["dependencies"] = []
        for dependency in dependencies:
            data["dependencies"].append({"quest": dependency.dependency_id,
                                         "type": dependency.type})

        data["sentences"] = []
        count = 0
        for sentence in sentences:
            data["sentences"].append({"dialogue": dialogue,
                                      "sentence": count,
                                      "ordinal": sentence.ordinal,
                                      "speaker": sentence.speaker,
                                      "content": sentence.content,
                                      "action": sentence.action,
                                      "provide_quest": sentence.provide_quest_id,
                                      "complete_quest": sentence.complete_quest_id})
            count += 1

        data["sentences"].sort(key=lambda x:x["ordinal"])

        data["nexts"] = [next.next.key for next in nexts]

        # Add to cache.
        self.dialogue_storage[dialogue] = data


    def get_dialogue(self, dialogue):
        """
        Get specified dialogue.
        """
        if not dialogue:
            return

        # Load cache.
        self.load_cache(dialogue)

        if not dialogue in self.dialogue_storage:
            # Can not find dialogue.
            return

        return self.dialogue_storage[dialogue]


    def get_sentence(self, dialogue, sentence):
        """
        Get specified sentence.
        """
        dlg = self.get_dialogue(dialogue)

        try:
            return dlg["sentences"][sentence]
        except Exception, e:
            pass

        return


    def get_sentences(self, caller, npc):
        """
        Get NPC's sentences.
        """
        if not caller:
            return

        if not npc:
            return

        sentences = []

        # Get npc's dialogues.
        for dlg_key in npc.dialogues:
            # Get all dialogues.
            npc_dlg = self.get_dialogue(dlg_key)
            if not npc_dlg:
                continue

            # Match conditions.
            if not SCRIPT_HANDLER.match_condition(caller, npc, npc_dlg["condition"]):
                continue

            # Match dependeces.
            match = True
            for dep in npc_dlg["dependencies"]:
                if not QUEST_DEP_HANDLER.match_dependency(caller, dep["quest"], dep["type"]):
                    match = False
                    break;
            if not match:
                continue

            if npc_dlg["sentences"]:
                # If has sentence, use it.
                sentences.append(npc_dlg["sentences"][0])

        if not sentences:
            # Use default sentences.
            # Default sentences should not have condition and dependencies.
            for dlg_key in npc.default_dialogues:
                npc_dlg = self.get_dialogue(dlg_key)
                if npc_dlg:
                    sentences.append(npc_dlg["sentences"][0])
            
        return sentences


    def get_next_sentences(self, caller, npc, current_dialogue, current_sentence):
        """
        Get current sentence's next sentences.
        """
        if not caller:
            return

        # Get current dialogue.
        dlg = self.get_dialogue(current_dialogue)
        if not dlg:
            return

        sentences = []

        try:
            # If has next sentence, use next sentence.
            sentences.append(dlg["sentences"][current_sentence + 1])
        except Exception, e:
            # Else get next dialogues.
            for dlg_key in dlg["nexts"]:
                # Get next dialogue.
                next_dlg = self.get_dialogue(dlg_key)
                if not next_dlg:
                    continue

                if not next_dlg["sentences"]:
                    continue

                if not SCRIPT_HANDLER.match_condition(caller, npc, next_dlg["condition"]):
                    continue

                for dep in next_dlg["dependencies"]:
                    if not QUEST_DEP_HANDLER.match_dependency(caller, dep["quest"], dep["type"]):
                        continue

                sentences.append(next_dlg["sentences"][0])

        return sentences

        
    def get_dialogue_speaker(self, caller, npc, speaker_str):
        """
        Get the speaker's text.
        'p' means player.
        'n' means NPC.
        Use string in quotes directly.
        """
        speaker = ""
        try:
            if speaker_str == "n":
                speaker = npc.get_name()
            elif speaker_str == "p":
                speaker = caller.get_name()
            elif speaker_str[0] == '"' and speaker_str[-1] == '"':
                speaker = speaker_str[1:-1]
        except:
            pass

        return speaker


    def finish_sentence(self, caller, npc, dialogue, sentence):
        """
        A sentence finished, do it's action.
        """
        if not caller:
            return
        
        # get dialogue
        dlg = self.get_dialogue(dialogue)
        if not dlg:
            return

        if sentence >= len(dlg["sentences"]):
            return

        sen = self.get_sentence(dialogue, sentence)
        if not sen:
            return

        # do dialogue's action
        if sen["action"]:
            SCRIPT_HANDLER.do_action(caller, npc, sen["action"])

        if sentence + 1 >= len(dlg["sentences"]):
            # last sentence
            self.finish_dialogue(caller, dialogue)

        if sen["complete_quest"]:
            caller.quest.complete(sen["complete_quest"])

        if sen["provide_quest"]:
            caller.quest.accept(sen["provide_quest"])


    def finish_dialogue(self, caller, dialogue):
        """
        A dialogue finished, do it's action.
        args:
            caller(object): the dialogue caller
            dialogue(string): dialogue's key
        """
        if not caller:
            return

        caller.quest.at_objective(defines.OBJECTIVE_TALK, dialogue)


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


    def get_npc_name(self, dialogue):
        """
        Get who says this dialogue.
        """
        model_npc_dialogues = get_model(settings.WORLD_DATA_APP, settings.NPC_DIALOGUES)
        if model_npc_dialogues:
            # Get record.
            try:
                record = model_npc_dialogues.objects.get(dialogue=dialogue)
                return record.npc.name
            except Exception, e:
                pass

        return ""


    def have_quest(self, caller, npc):
        """
        Check if the npc can complete or provide quests.
        Completing is higher than providing.
        """
        provide_quest = False
        complete_quest = False

        if not caller:
            return (provide_quest, complete_quest)

        if not npc:
            return (provide_quest, complete_quest)

        accomplished_quests = caller.quest.get_accomplished_quests()

        # get npc's default dialogues
        for dlg_key in npc.dialogues:
            # find quests by recursion
            provide, complete = self.dialogue_have_quest(caller, npc, dlg_key, accomplished_quests)
                
            provide_quest = (provide_quest or provide)
            complete_quest = (complete_quest or complete)

            if complete_quest:
                break

            if not accomplished_quests:
                if provide_quest:
                    break
        
        return (provide_quest, complete_quest)


    def dialogue_have_quest(self, caller, npc, dialogue, accomplished_quests):
        """
        Find quests by recursion.
        """
        provide_quest = False
        complete_quest = False

        # check if the dialogue is available
        npc_dlg = self.get_dialogue(dialogue)
        if not npc_dlg:
            return (provide_quest, complete_quest)

        if not SCRIPT_HANDLER.match_condition(caller, npc, npc_dlg["condition"]):
            return (provide_quest, complete_quest)

        match = True
        for dep in npc_dlg["dependencies"]:
            if not QUEST_DEP_HANDLER.match_dependency(caller, dep["quest"], dep["type"]):
                match = False
                break;
        if not match:
            return (provide_quest, complete_quest)

        # find quests in its sentences
        for sen in npc_dlg["sentences"]:
            if sen["complete_quest"] in accomplished_quests:
                complete_quest = True
                return (provide_quest, complete_quest)

            if not provide_quest and sen["provide_quest"]:
                quest_key = sen["provide_quest"]
                if caller.quest.can_provide(quest_key):
                    provide_quest = True
                    if not accomplished_quests:
                        return (provide_quest, complete_quest)

        for dlg_key in npc_dlg["nexts"]:
            # get next dialogue
            provide, complete = self.dialogue_have_quest(caller, npc, dlg_key, accomplished_quests)
                
            provide_quest = (provide_quest or provide)
            complete_quest = (complete_quest or complete)

            if complete_quest:
                break

            if not accomplished_quests:
                if provide_quest:
                    break

        return (provide_quest, complete_quest)


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()
