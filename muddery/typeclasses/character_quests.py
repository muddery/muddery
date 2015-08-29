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
        self.obj_types = set()


    def at_init(self):
        """
        Load quest data.
        """
        super(MudderyQuest, self).at_init()

        self.objectives = {}
        self.obj_types = set()


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
            self.db.finished[obj_record.ordinal] = 0
            self.obj_types.add(obj_record.type)


    def finished(self):
        """
        """
        for key in self.objectives:
            obj_num = self.objectives[key]["number"]
            finished = self.db.finished.get(key, 0)
    
            if finished < obj_num:
                return False

        return True


    def at_character_move_in(self, location):
        """
        """
        for objective in self.objectives:
            if objective["type"] == "reach":
                if objective["object"] == location:
                    self.db.finished[objective["ordinal"]] += 1
                    break

