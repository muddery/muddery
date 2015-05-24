"""
DialogueHandler

"""

import re
from django.conf import settings
from django.db.models.loading import get_model


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
        arg = arg.split(":", 1)
        base_sentence = 1

        if len(arg) == 1:
            sentence = int(arg[0]) if arg[0] else base_sentence
        elif len(arg) == 2:
            dialogue = arg[0]
            sentence = int(arg[1]) if arg[1] else base_sentence
    
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
        current_dialogue = self.get_dialogue(current_dialogue, current_sentence)

        candidates = []

        # get availabel dialogues
        if current_dialogue:
            candidates = current_dialogue["next"].split(",")

        if not candidates:
            if npc:
                if npc.dialogue:
                    dialogues = npc.dialogue.split(",")
                    candidates = [dialogue + ":" for dialogue in dialogues]

        dialogues = []
        for candidate in candidates:
            parser = self.dialogue_arg_parser(candidate, current_dialogue)
            if parser:
                dlg = self.get_dialogue(parser[0], parser[1])
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

        re_words = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
        condition = re_words.sub("caller.\1", condition)
        try:
            match = eval(condition, {"caller": caller})
        except Exception, e:
            return false
            
        return match


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


# main dialoguehandler
DIALOGUE_HANDLER = DialogueHandler()
