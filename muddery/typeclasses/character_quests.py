"""
Quests
"""

from muddery.typeclasses.objects import MudderyObject
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
        self.db.finished = {}
        self.objectives = {}
        self.obj_unfinished = {}


    def at_init(self):
        """
        Load quest data.
        """
        self.objectives = {}
        self.obj_unfinished = {}
        super(MudderyQuest, self).at_init()


    def load_data(self):
        """
        """
        super(MudderyQuest, self).load_data()

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
                         "number": obj_record.number}
            self.objectives[obj_record.ordinal] = objective

            finished = self.db.finished.get(key, 0)
            if finished < obj_record.number:
                if not obj_record.type in self.obj_unfinished:
                    self.obj_unfinished[obj_record.type] = [obj_record.ordinal]
                else:
                    self.obj_unfinished[obj_record.type].append(obj_record.ordinal)


    def finished(self):
        """
        """
        for ordinal in self.objectives:
            obj_num = self.objectives[ordinal]["number"]
            finished = self.db.finished.get(ordinal, 0)
    
            if finished < obj_num:
                return False

        return True


    def at_talk_finished(self, dialogue):
        """
        """
        if not OBJECTIVE_TALK in self.obj_unfinished:
            return False

        status_changed = False
        index = 0
        while index < len(self.obj_unfinished[OBJECTIVE_TALK]):
            ordinal = self.obj_unfinished[OBJECTIVE_TALK][index]
            index += 1

            if self.objectives[ordinal]["object"] == dialogue:
                finished = self.db.finished.get(ordinal, 0)
                finished += 1
                self.db.finished[ordinal] = finished

                if self.db.finished[ordinal] >= self.objectives[ordinal]["number"]:
                    # finished
                    self.obj_unfinished.remove(ordinal)
                    index -= 1

                    if not self.obj_unfinished[OBJECTIVE_TALK]:
                        del(self.obj_unfinished[OBJECTIVE_TALK])
                        break

                status_changed = True

        return status_changed
