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

import re
from muddery.utils import defines
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
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
        data["have_quest"] = dialogue_record.have_quest

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
                                      "provide_quest": sentence.provide_quest_id})
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
        if npc:
            for dlg_key in npc.dialogues:
                npc_dlg = self.get_dialogue(dlg_key)
                if not npc_dlg:
                    continue

                if not self.match_condition(caller, npc_dlg["condition"]):
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


    def get_next_sentences(self, caller, npc, current_dialogue, current_sentence):
        """
        """
        if not caller:
            return

        if not npc:
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

                if not self.match_condition(caller, next_dlg["condition"]):
                    continue

                for dep in next_dlg["dependences"]:
                    if not QUEST_DEP_HANDLER.match_dependence(caller, dep["quest"], dep["type"]):
                        continue

                sentences.append(next_dlg["sentences"][0])

        return sentences


    def match_condition(self, caller, condition):
        """
        check condition
        """
        if not condition:
            return True

        # add "caller" to condition
        condition = self.safe_statement(condition)

        try:
            # check it
            match = eval(condition, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("match_condition error:%s %s" % (condition, e))
            return False

        return match


    def finish_sentence(self, caller, dialogue, sentence):
        """
        A sentence finished, do it's action.
        """
        if not caller:
            return
        
        # get dialogue
        dlg = self.get_sentence(dialogue, sentence)
        if not dlg:
            return

        # do dialogue's action
        if dlg["action"]:
            self.do_action(caller, dlg["action"])

        if dlg["provide_quest"]:
            caller.quest.accept(dlg["provide_quest"])


    def do_action(self, caller, action):
        """
        do action
        """

        if not action:
            return

        # add "caller" to action
        action = self.safe_statement(action)

        # run action
        try:
            eval(action, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("do_dialogue_action error:%s %s" % (action, e))
            
        return


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


    re_words = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)|(\"(.*?)\")")
    def safe_statement(self, statement):
        """
        Add "caller." before every words.
        """
        return self.re_words.sub(self.sub_statement, statement)


    statement_keywords = {"not", "and", "or"}
    def sub_statement(self, match):
        """
        Replace <match> with caller.<match> except key words.
        """
        match = match.group()

        # keep the key words
        if match in self.statement_keywords:
            return match

        # keep the strings in quotes
        if match[0] == "\"" and match[-1] == "\"":
            return match

        return "caller." + match


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()
