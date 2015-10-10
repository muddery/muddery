"""
DialogueHandler

The DialogueHandler maintains a pool of dialogues.

All dialogues are stored in WORLD_DATA_APP's DIALOGUES like this:
+----------+----------+---------+---------+------+-----------+---------+
| dialogue | sentence | speaker | content | next | condition | action  |
+----------+----------+---------+---------+------+-----------+---------+
| dia_01   | 1        | p       | Hello!  | 2    | hp > 0    | hp += 1 |
+----------+----------+---------+---------+------+-----------+---------+

dialogue:   string, is the dialogue's id. A dialogue can have several sentences.
sentence:   number, the serial number of sentence. It may not be continuous.
speaker:    string, "p" refers to the player, "n" refers to the NPC, others refers to blank.
content:    string, sentence's content, it can contains color marks.
next:       string, refers to next sentences, in format of
            "[<dialogue id>:]<sentence>, [<dialogue id>:]<sentence>, [<dialogue id>:]<sentence> ..."
            Example:
              "dlg03:5" means dialogue: dlg03, sentence: 5
              "dlg03:"  means dialogue: dlg03, sentence: 1
              ":5"      means current_dlg, sentence: 5
              "5"       means current_dlg, sentence: 5
              ""        means current_dlg, current sentence + 1
              "-1"      means no next sentence
            It can be a series of sentences. Only the ones which matches the condition will be display.
            If there are several sentences can display, all these sentences will send to the player for
            selection.
condition:  string, sentence's condition. The condition is a logical expression.
            The sentence will not display, if the condition is not matched.
            "caller." will be add before every words in the condition. For example,
            "hp" will become "caller.hp". Dialogue can use caller's variables and methords
            in this way. Dialogue can only use first level variables, for "db.hp" will become
            "caller.db.caller.hp". And it is safe because "os.system" will become
            "caller.os.caller.system".
action:     string, sentence's action. It will be run when the sentence is used. If there
            are several sentences provided to the player at the same time, it will only run
            the one which the player select. It is a statement. "caller." will be add to every
            words in the action, like condition.
"""


from muddery.utils import defines
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
from muddery.utils import script_handler
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class DialogueHandler(object):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize handler
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

        dependences = []
        model_dependences = get_model(settings.WORLD_DATA_APP, settings.DIALOGUE_QUEST_DEPENDENCY)
        if model_dependences:
            # Get records.
            dependences = model_dependences.objects.filter(dialogue=dialogue)


        # Add db fields to data object.
        data = {}

        data["condition"] = dialogue_record.condition

        data["dependences"] = []
        for dependence in dependences:
            data["dependences"].append({"quest": dependence.dependence_id,
                                        "type": dependence.type})

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
                                      "finish_quest": sentence.finish_quest_id})
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

        # load cache
        self.load_cache(dialogue)

        if not dialogue in self.dialogue_storage:
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


    def get_default_sentences(self, caller, npc):
        """
        """
        if not caller:
            return

        if not npc:
            return

        sentences = []

        # get npc's default dialogues
        for dlg_key in npc.dialogues:
            npc_dlg = self.get_dialogue(dlg_key)
            if not npc_dlg:
                continue

            if not script_handler.match_condition(caller, npc_dlg["condition"]):
                continue

            match = True
            for dep in npc_dlg["dependences"]:
                if not QUEST_DEP_HANDLER.match_dependence(caller, dep["quest"], dep["type"]):
                    match = False
                    break;
            if not match:
                continue

            if npc_dlg["sentences"]:
                # if has sentence, use it
                sentences.append(npc_dlg["sentences"][0])

        return sentences


    def get_next_sentences(self, caller, current_dialogue, current_sentence):
        """
        """
        if not caller:
            return

        # get current dialogue
        dlg = self.get_dialogue(current_dialogue)
        if not dlg:
            return

        sentences = []

        try:
            # if has next sentence, use next sentence
            sentences.append(dlg["sentences"][current_sentence + 1])
        except Exception, e:
            # get next dialogues
            for dlg_key in dlg["nexts"]:
                # get next dialogue
                next_dlg = self.get_dialogue(dlg_key)
                if not next_dlg:
                    continue

                if not next_dlg["sentences"]:
                    continue

                if not script_handler.match_condition(caller, next_dlg["condition"]):
                    continue

                for dep in next_dlg["dependences"]:
                    if not QUEST_DEP_HANDLER.match_dependence(caller, dep["quest"], dep["type"]):
                        continue

                sentences.append(next_dlg["sentences"][0])

        return sentences

        
    def get_dialogue_speaker(self, caller, npc, speaker_str):
        """
        Get the speaker's text.
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


    def finish_sentence(self, caller, dialogue, sentence):
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
            script_handler.do_action(caller, sen["action"])

        if sentence + 1 >= len(dlg["sentences"]):
            # last sentence
            self.finish_dialogue(caller, dialogue)

        if sen["finish_quest"]:
            caller.quest.finish(sen["finish_quest"])

        if sen["provide_quest"]:
            caller.quest.accept(sen["provide_quest"])


    def finish_dialogue(self, caller, dialogue):
        """
        A dialogue finished, do it's action.
        """
        if not caller:
            return

        caller.quest.at_talk_finished(dialogue)


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


    def get_npc_name(self, dialogue):
        """
        Get who say this dialogue.
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
        check if the npc can finish or provide quests
        finishing is higher than providing
        """
        provide_quest = False
        finish_quest = False

        if not caller:
            return (provide_quest, finish_quest)

        if not npc:
            return (provide_quest, finish_quest)

        achieved_quests = caller.quest.get_achieved_quests()

        # get npc's default dialogues
        for dlg_key in npc.dialogues:
            # find quests by recursion
            provide, finish = self.dialogue_have_quest(caller, npc, dlg_key, achieved_quests)
                
            provide_quest = (provide_quest or provide)
            finish_quest = (finish_quest or finish)

            if finish_quest:
                break

            if not achieved_quests:
                if provide_quest:
                    break
        
        return (provide_quest, finish_quest)


    def dialogue_have_quest(self, caller, npc, dialogue, achieved_quests):
        """
        find quests by recursion
        """
        provide_quest = False
        finish_quest = False

        # check if the dialogue is available
        npc_dlg = self.get_dialogue(dialogue)
        if not npc_dlg:
            return (provide_quest, finish_quest)

        if not script_handler.match_condition(caller, npc_dlg["condition"]):
            return (provide_quest, finish_quest)

        match = True
        for dep in npc_dlg["dependences"]:
            if not QUEST_DEP_HANDLER.match_dependence(caller, dep["quest"], dep["type"]):
                match = False
                break;
        if not match:
            return (provide_quest, finish_quest)

        # find quests in its sentences
        for sen in npc_dlg["sentences"]:
            if sen["finish_quest"] in achieved_quests:
                finish_quest = True
                return (provide_quest, finish_quest)

            if not provide_quest and sen["provide_quest"]:
                quest_key = sen["provide_quest"]
                if caller.quest.can_provide(quest_key):
                    provide_quest = True
                    if not achieved_quests:
                        return (provide_quest, finish_quest)

        for dlg_key in npc_dlg["nexts"]:
            # get next dialogue
            provide, finish = self.dialogue_have_quest(caller, npc, dlg_key, achieved_quests)
                
            provide_quest = (provide_quest or provide)
            finish_quest = (finish_quest or finish)

            if finish_quest:
                break

            if not achieved_quests:
                if provide_quest:
                    break

        return (provide_quest, finish_quest)


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()
