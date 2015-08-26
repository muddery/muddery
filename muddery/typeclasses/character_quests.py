"""
Quests
"""

from muddery.typeclasses.objects import MudderyObject
from django.conf import settings
from django.db.models.loading import get_model


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

        # need save before modify m2m fields
        self.save()

        try:
            self.load_data()
        except Exception, e:
            logger.log_errmsg("%s can not load data:%s" % (self.dbref, e))

    
    def load_data(self):
        """
        """
        super(MudderyQuest, self).load_data()

        key = self.get_info_key()
        if not key:
            return

        objectives = []
        model_objectives = get_model(settings.WORLD_DATA_APP, settings.QUEST_OBJECTIVES)
        if model_objectives:
            # Get records.
            objectives = model_objectives.objects.filter(quest=key)

        for objective in objectives:
            obj = {"ordinal": objective.ordinal,
                   "type": objective.type,
                   "object": objective.object,
                   "number": objective.number}
            self.objectives[objective.ordinal] = obj
            self.obj_types.add(objective.type)
            self.db.finished[objective.ordinal] = 0


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

