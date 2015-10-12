"""
Quests
"""

from muddery.utils import defines
from muddery.typeclasses.objects import MudderyObject
from muddery.utils import script_handler
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.localized_strings_handler import LS
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class MudderyQuest(MudderyObject):
    """
    """
    def at_object_creation(self):
        """
        Set default values.
        """
        self.db.achieved = {}


    def load_data(self):
        """
        """
        super(MudderyQuest, self).load_data()

        self.objectives = {}
        self.not_achieved = {}
        
        key = self.get_info_key()
        if not key:
            return

        obj_records = []
        model_objectives = get_model(settings.WORLD_DATA_APP, settings.QUEST_OBJECTIVES)
        if model_objectives:
            # Get records.
            obj_records = model_objectives.objects.filter(quest=key)

        for obj_record in obj_records:
            objective = {"ordinal": obj_record.ordinal,
                         "type": obj_record.type,
                         "object": obj_record.object,
                         "number": obj_record.number,
                         "desc": obj_record.desc}
            self.objectives[obj_record.ordinal] = objective

            achieved = self.db.achieved.get(key, 0)
            if achieved < obj_record.number:
                if not obj_record.type in self.not_achieved:
                    self.not_achieved[obj_record.type] = [obj_record.ordinal]
                else:
                    self.not_achieved[obj_record.type].append(obj_record.ordinal)


    def return_objectives(self):
        """
        """
        objectives = []
        for ordinal in self.objectives:
            desc = self.objectives[ordinal]["desc"]
            if desc:
                objectives.append({"desc": self.objectives[ordinal]["desc"]})
            else:
                obj_num = self.objectives[ordinal]["number"]
                achieved = self.db.achieved.get(ordinal, 0)
                
                if self.objectives[ordinal]["type"] == defines.OBJECTIVE_TALK:
                    target = LS("Talk to")
                    object = DIALOGUE_HANDLER.get_npc_name(self.objectives[ordinal]["object"])
        
                    objectives.append({"target": target,
                                       "object": object,
                                       "achieved": achieved,
                                       "total": obj_num,
                                       })

        return objectives


    def is_achieved(self):
        """
        """
        for ordinal in self.objectives:
            obj_num = self.objectives[ordinal]["number"]
            achieved = self.db.achieved.get(ordinal, 0)
    
            if achieved < obj_num:
                return False

        return True


    def finish(self):
        """
        """
        # do quest's action
        if self.action:
            script_handler.do_action(caller, self.action)


    def at_talk_finished(self, dialogue):
        """
        """
        if not defines.OBJECTIVE_TALK in self.not_achieved:
            return False

        status_changed = False
        index = 0
        while index < len(self.not_achieved[defines.OBJECTIVE_TALK]):
            ordinal = self.not_achieved[defines.OBJECTIVE_TALK][index]
            index += 1

            if self.objectives[ordinal]["object"] == dialogue:
                status_changed = True

                achieved = self.db.achieved.get(ordinal, 0)
                achieved += 1
                self.db.achieved[ordinal] = achieved

                if self.db.achieved[ordinal] >= self.objectives[ordinal]["number"]:
                    # objective achieved
                    del(self.not_achieved[defines.OBJECTIVE_TALK][ordinal])
                    index -= 1

                    if not self.not_achieved[defines.OBJECTIVE_TALK]:
                        del(self.not_achieved[defines.OBJECTIVE_TALK])
                        break

        # if status_changed:
        #     if self.is_objectives_achieved():
        #         self.finish()

        return status_changed
