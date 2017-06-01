"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

"""

from __future__ import print_function

import re
from muddery.utils import defines
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS
from evennia.utils import logger


class DialogueHandler(object):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    speaker_escape = re.compile(r'%[%|p|n]')

    @staticmethod
    def escape_fun(word):
        """
        Change escapes to target words.
        """
        escape_word = word.group()
        char = escape_word[1]
        if char == "%":
            return char
        else:
            return "%(" + char + ")s"

    def __init__(self):
        """
        Initialize the handler.
        """
        self.can_close_dialogue = GAME_SETTINGS.get("can_close_dialogue")
        self.single_sentence_mode = GAME_SETTINGS.get("single_dialogue_sentence")
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
            dialogue_record = DATA_SETS.dialogues.objects.get(key=dialogue)
        except Exception, e:
            return

        sentences = DATA_SETS.dialogue_sentences.objects.filter(dialogue=dialogue)

        nexts = DATA_SETS.dialogue_relations.objects.filter(dialogue=dialogue)

        dependencies = DATA_SETS.dialogue_quest_dependencies.objects.filter(dialogue=dialogue)

        # Add db fields to data object.
        data = {}

        data["condition"] = dialogue_record.condition

        data["dependencies"] = []
        for dependency in dependencies:
            data["dependencies"].append({"quest": dependency.dependency,
                                         "type": dependency.type})

        data["sentences"] = []
        for sentence in sentences:
            speaker_model = self.speaker_escape.sub(self.escape_fun, sentence.speaker)

            data["sentences"].append({"dialogue": dialogue,
                                      "ordinal": sentence.ordinal,
                                      "speaker_model": speaker_model,
                                      "icon": sentence.icon,
                                      "content": sentence.content,
                                      "action": sentence.action,
                                      "provide_quest": sentence.provide_quest,
                                      "complete_quest": sentence.complete_quest,
                                      "can_close": self.can_close_dialogue})

        # sort sentences by ordinal
        data["sentences"].sort(key=lambda x:x["ordinal"])
        count = 0
        for sentence in data["sentences"]:
            sentence["sentence"] = count
            sentence["is_last"] = False
            count += 1
        data["sentences"][-1]["is_last"] = True

        data["nexts"] = [next_one.next_dlg for next_one in nexts]

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

    def check_need_get_next(self, sentences):
        """
        Check if the next sentence can be added to the sentence list.
        If a sentence will effect the character's status, it should not be
        added to the sentence list.
        """
        if self.single_sentence_mode:
            return False

        if len(sentences) != 1:
            return False

        sentence = sentences[0]
        if sentence['is_last'] or\
           sentence['action'] or\
           sentence['complete_quest'] or\
           sentence['provide_quest']:
            return False

        return True

    def get_npc_sentences_list(self, caller, npc):
        """
        Get a sentences list to send to the caller at one time.
        
        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.
        
        Returns:
            sentences_list: (list) a list of sentences that can be show in order.
        """
        if not caller:
            return []

        if not npc:
            return []

        sentences_list = []

        # Get the first sentences.
        sentences = self.get_npc_sentences(caller, npc)
        output = self.create_output_sentences(sentences, caller, npc)
        if output:
            sentences_list.append(output)
        else:
            return sentences_list

        # Get next sentences.
        while self.check_need_get_next(sentences):
            sentences = self.get_next_sentences(caller,
                                                npc.dbref,
                                                sentences[0]['dialogue'],
                                                sentences[0]['sentence'])
            output = self.create_output_sentences(sentences, caller, npc)
            if output:
                sentences_list.append(output)
            else:
                break

        return sentences_list

    def get_next_sentences_list(self, caller, npc, dialogue, sentence, include_current):
        """
        Get a sentences list from the current sentence.
        
        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.
            dialogue: (string) the key of the currrent dialogue.
            sentence: (int) the number of current sentence.
            include_current: (boolean) if the sentence list includes current sentence.

        Returns:
            sentences_list: (list) a list of sentences that can be show in order.
        """
        sentences_list = []

        # current sentence
        sentences = []
        if include_current:
            data = self.get_sentence(dialogue, sentence)
            if data:
                sentences = [data]
        else:
            sentences = self.get_next_sentences(caller,
                                                npc,
                                                dialogue,
                                                sentence)
        output = self.create_output_sentences(sentences, caller, npc)
        if output:
            sentences_list.append(output)

        while self.check_need_get_next(sentences):
            sentences = self.get_next_sentences(caller,
                                                npc,
                                                sentences[0]['dialogue'],
                                                sentences[0]['sentence'])
            output = self.create_output_sentences(sentences, caller, npc)
            if output:
                sentences_list.append(output)
            else:
                break

        return sentences_list

    def get_npc_sentences(self, caller, npc):
        """
        Get NPC's sentences that can show to the caller.

        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.

        Returns:
            sentences: (list) a list of available sentences.
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
            if not STATEMENT_HANDLER.match_condition(npc_dlg["condition"], caller, npc):
                continue

            # Match dependencies.
            match = True
            for dep in npc_dlg["dependencies"]:
                if not QUEST_DEP_HANDLER.match_dependency(caller, dep["quest"], dep["type"]):
                    match = False
                    break
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
        
        Args:
            caller: (object) the character who want to start a talk.
            npc: (object) the NPC that the character want to talk to.
            dialogue: (string) the key of the currrent dialogue.
            sentence: (int) the number of current sentence.

        Returns:
            sentences: (list) a list of available sentences.
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

                if not STATEMENT_HANDLER.match_condition(next_dlg["condition"], caller, npc):
                    continue

                for dep in next_dlg["dependencies"]:
                    if not QUEST_DEP_HANDLER.match_dependency(caller, dep["quest"], dep["type"]):
                        continue

                sentences.append(next_dlg["sentences"][0])

        return sentences

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
            try:
                resource_info = DATA_SETS.icon_resources.objects.get(key=icon_str)
                icon = resource_info.resource.name
            except Exception, e:
                logger.log_errmsg("Load icon %s error: %s" % (icon_str, e))
        else:
            if "%(n)" in speaker_model:
                if npc:
                    icon = getattr(npc, "icon", None)
            elif "%(p)" in speaker_model:
                icon = getattr(caller, "icon", None)

        return icon

    def create_output_sentences(self, originals, caller, npc):
        """
        Transform the sentences from the storing format to the output format.

        Args:
            originals: (list) original sentences data
            caller: (object) caller object
            npc: (object, optional) NPC object

        Returns:
            (list) a list of sentence's data
        """
        if not originals:
            return []

        sentences_list = []
        speaker = self.get_dialogue_speaker_name(caller, npc, originals[0]["speaker_model"])
        icon = self.get_dialogue_speaker_icon(originals[0]["icon"], caller, npc, originals[0]["speaker_model"])
        for original in originals:
            sentence = {"speaker": speaker,             # speaker's name
                        "dialogue": original["dialogue"],   # dialogue's key
                        "sentence": original["sentence"],   # sentence's ordinal
                        "content": original["content"],
                        "icon": icon,
                        "can_close": original["can_close"],}
            if npc:
                sentence["npc"] = npc.dbref             # NPC's dbref
            else:
                sentence["npc"] = ""

            sentences_list.append(sentence)

        return sentences_list

    def finish_sentence(self, caller, npc, dialogue, sentence_no):
        """
        A sentence finished, do it's action.
        """
        if not caller:
            return
        
        # get dialogue
        dlg = self.get_dialogue(dialogue)
        if not dlg:
            return

        if sentence_no >= len(dlg["sentences"]):
            return

        sentence = self.get_sentence(dialogue, sentence_no)
        if not sentence:
            return

        # do dialogue's action
        if sentence["action"]:
            STATEMENT_HANDLER.do_action(sentence["action"], caller, npc)

        if sentence["is_last"]:
            # last sentence
            self.finish_dialogue(caller, dialogue)

        if sentence["complete_quest"]:
            caller.quest_handler.complete(sentence["complete_quest"])

        if sentence["provide_quest"]:
            caller.quest_handler.accept(sentence["provide_quest"])

    def finish_dialogue(self, caller, dialogue):
        """
        A dialogue finished, do it's action.
        args:
            caller(object): the dialogue caller
            dialogue(string): dialogue's key
        """
        if not caller:
            return

        caller.quest_handler.at_objective(defines.OBJECTIVE_TALK, dialogue)

    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}

    def get_npc_name(self, dialogue):
        """
        Get who says this dialogue.
        """
        # Get record.
        try:
            record = DATA_SETS.npc_dialogues.objects.get(dialogue=dialogue)
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

        accomplished_quests = caller.quest_handler.get_accomplished_quests()

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

        if not STATEMENT_HANDLER.match_condition(npc_dlg["condition"], caller, npc):
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
                if caller.quest_handler.can_provide(quest_key):
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
