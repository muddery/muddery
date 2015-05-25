"""
DialogueHandler

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
        """
        if not dialogue:
            return

        if hasattr(self.dialogue_storage, dialogue):
            # already cached
            return

        # add cache
        self.dialogue_storage[dialogue] = {}
        
        # Get db model
        objects = []
        for model in settings.DIALOGUES:
            model_obj = get_model(settings.WORLD_DATA_APP, model)
            if model_obj:
                # Get dialogue records.
                objects = model_obj.objects.filter(dialogue=dialogue)
                if objects:
                    break
        
        if not objects:
            return
        
        for obj in objects:
            data = {"dialogue": obj.dialogue,
                    "sentence": obj.sentence,
                    "speaker": obj.speaker,
                    "content": obj.content,
                    "next": obj.next,
                    "condition": obj.condition,
                    "action": obj.action}
            self.dialogue_storage[dialogue][obj.sentence] = data


    def get_dialogue(self, dialogue, sentence):
        """
        """
        if not dialogue and not sentence:
            return

        self.add_cache(dialogue)

        try:
            # try to use cache
            return self.dialogue_storage[dialogue][sentence]
        except Exception, e:
            return
    

    def dialogue_arg_parser(self, arg, current_dlg=None):
        """
        get npc's dialogue

        arg: string [<dialogue id>:]<sentence>
             example: "dlg03:5" means dialogue: dlg03, sentence: 5
                      "dlg03:"  means dialogue: dlg03, sentence: 1
                      ":5"      means current_dlg, sentence: 5
                      "5"       means current_dlg, sentence: 5
                      ""        means current_dlg, next sentence
        """
        sentence = ""
        dialogue = ""

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
            if npc:
                if npc.dialogue:
                    dialogues = npc.dialogue.split(",")
                    candidates = [dialogue + ":" for dialogue in dialogues]

        dialogues = []
        for candidate in candidates:
            parser = self.dialogue_arg_parser(candidate, current)
            if parser:
                dlg = self.get_dialogue(parser[0], int(parser[1]))
                if dlg:
                    if self.match_condition(caller, dlg["condition"]):
                        # parser speaker
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
        check the condition
        """
        if not condition:
            return True

        condition = self.safe_statement(condition)
        try:
            match = eval(condition, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("match_condition error:%s %s" % (condition, e))
            return False
            
        return match


    def do_dialogue_action(self, caller, dialogue, sentence):
        """
        do action
        """
        current = self.get_dialogue(dialogue, sentence)
        if not current:
            return

        self.do_action(caller, current["action"])


    def do_action(self, caller, action):
        """
        do action
        """
        if not action:
            return

        action = self.safe_statement(action)
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


    re_words = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)")
    def safe_statement(self, statement):
        """
        """
        return self.re_words.sub(self.sub_statement, statement)


    statement_keywords = {"not", "and", "or"}
    def sub_statement(self, match):
        """
        """
        match = match.group()
        if match in self.statement_keywords:
            return match

        return "caller." + match


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()
