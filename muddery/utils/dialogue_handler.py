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
    
    
    def add_cache(self, dialogue):
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
        objects = []
        model_obj = get_model(settings.WORLD_DATA_APP, settings.DIALOGUES)
        if model_obj:
            # Get dialogue records.
            objects = model_obj.objects.filter(dialogue=dialogue)

        for obj in objects:
            # Add db fields to dict.
            data = {"dialogue": obj.dialogue,
                    "sentence": obj.sentence,
                    "speaker": obj.speaker,
                    "content": obj.content,
                    "next": obj.next,
                    "condition": obj.condition,
                    "action": obj.action}

            # Add to cache.
            self.dialogue_storage[dialogue][obj.sentence] = data


    def get_dialogue(self, dialogue, sentence):
        """
        Get specified sentence.
        """
        if not dialogue and not sentence:
            return

        # load cache
        self.add_cache(dialogue)

        try:
            # get data in cache
            return self.dialogue_storage[dialogue][sentence]
        except Exception, e:
            return
    

    def dialogue_arg_parser(self, arg, current_dlg=None):
        """
        parse the arg into (dialogue, sentence,)

        arg: string [<dialogue id>:]<sentence>
             example: "dlg03:5" means dialogue: dlg03, sentence: 5
                      "dlg03:"  means dialogue: dlg03, sentence: 1
                      ":5"      means current_dlg, sentence: 5
                      "5"       means current_dlg, sentence: 5
                      ""        means current_dlg, current sentence + 1
                      "-1"      means no next sentence
        current_dlg: dict of the current dialogue.
        """
        sentence = ""
        dialogue = ""

        # parse the arg
        arg_list = arg.split(":", 1)
        if len(arg_list) == 1:
            sentence = arg_list[0]
        elif len(arg_list) == 2:
            dialogue = arg_list[0]
            sentence = arg_list[1]

        if not dialogue and not sentence:
            if current_dlg:
                dialogue = current_dlg["dialogue"]
                sentence = current_dlg["sentence"] + 1
            else:
                return
        elif not dialogue:
            if current_dlg:
                dialogue = current_dlg["dialogue"]
            else:
                return
            sentence = int(sentence)
        elif not sentence:
            sentence = 1

        return (dialogue, sentence,)


    def get_next_dialogue(self, caller, npc, current_dialogue, current_sentence):
        """
        get npc's next dialogue
        """
        current = self.get_dialogue(current_dialogue, current_sentence)

        candidates = []

        # get availabel dialogues
        if current:
            if current["next"]:
                candidates = current["next"].split(",")
            else:
                candidates = [unicode(current["sentence"] + 1)]

        if not candidates:
            # get npc's default dialogues.
            if npc:
                if npc.dialogue:
                    dialogues = npc.dialogue.split(",")
                    candidates = [dialogue + ":" for dialogue in dialogues]

        dialogues = []
        for candidate in candidates:
            parser = self.dialogue_arg_parser(candidate, current)
            if parser:
                # get dialogue
                dlg = self.get_dialogue(parser[0], parser[1])
                if dlg:
                    # check condition
                    if self.match_condition(caller, dlg["condition"]):
                        # speakers may be different to different players, so copy it.
                        dlg = dlg.copy()

                        # parse the speaker
                        if dlg["speaker"] == "p":
                            dlg["speaker"] = caller.name
                        elif dlg["speaker"] == "n":
                            dlg["speaker"] = npc.name
                        else:
                            dlg["speaker"] = ""

                        # add npc's dbref
                        dlg["npc"] = npc.dbref
                        dialogues.append(dlg)

        return dialogues


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


    def do_dialogue_action(self, caller, dialogue, sentence):
        """
        do dialogue's action
        """
        
        # get dialogue
        dlg = self.get_dialogue(dialogue, sentence)
        if not dlg:
            return

        # do dialogue's action
        self.do_action(caller, dlg["action"])


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
