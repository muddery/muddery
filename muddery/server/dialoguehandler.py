"""
DialogueHandler

"""

import re


class DialogueHandler(object):
    """
    The DialogueHandler maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.dialogue_storage = {}
    

    def get_dialogue(self, arg, current_dlg=None):
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

        if len(arg) == 1:
            sentence = int(arg[0])
        elif len(key) == 2:
            dialogue = arg[0]
            sentence = int(arg[1])
    
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

        try:
            # try to use cache
            return sentence.dialogue_storage[dialogue][sentence]
        except: Exception, e:
            # Get db model
            model_obj = get_model(settings.WORLD_DATA_APP, NPC_DIALOGUE)
            if not model_obj:
                return

            # Get data record.
            record = model_obj.objects.filter(dialogue=key, step=step)
            if not data:
                return

            record = record[0]
            data["dialogue"] = record[0].dialogue;
            data["sentence"] = record[0].sentence;

            # store to cache
            if not self.dialogue_storage.haskey(dialogue):
                self.dialogue_storage[dialogue] = {}
            self.dialogue_storage[dialogue][step] = data
    
            return data


    def get_next_dialogue(self, caller, npc, current_dlg):
        """
        get npc's next dialogue
        """
        candidates = []

        # get availabel dialogues
        if current_dlg:
            candidates = current_dlg["next"].split(",")

        if not candidates:
            if npc:
                dialogues = npc.dialogues.split(",")
                candidates = [dialogue + ":" for dialogue in dialogues]
        
        for candidate in candidates:
            dlg = self.get_dialogue(candidate)
            if dlg:
                if self.match_condition(caller, dlg["condition"]:
                    return dlg
                    
                    
    def match_condition(self, caller, condition):
        """
        check the condition
        """
        re_words = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
        condition = re_words.sub("caller.\1", condition)
        try:
            match = exec(condition)
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
