"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from muddery.utils import defines
from muddery.typeclasses.objects import MudderyObject
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.loot_handler import LootHandler
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from muddery.worlddata.data_sets import DATA_SETS
from django.conf import settings
from django.apps import apps
from evennia.utils import logger
from evennia.utils.utils import lazy_property


class MudderyQuest(MudderyObject):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, DATA_SETS.quest_reward_list.model)

    def at_object_creation(self):
        """
        Set accomplished objectives to empty.
        """
        super(MudderyQuest, self).at_object_creation()

        if not self.attributes.has("owner"):
            self.db.owner = None
        if not self.attributes.has("accomplished"):
            self.db.accomplished = {}

    def set_owner(self, owner):
        """
        Set the owner of the skill.
        """
        self.db.owner = owner

    def after_data_loaded(self):
        """
        Load quest's data from db.
        """
        super(MudderyQuest, self).after_data_loaded()

        self.objectives = {}
        self.not_accomplished = {}
        
        key = self.get_data_key()
        if not key:
            return

        # Get objectives.
        obj_records = DATA_SETS.quest_objectives.objects.filter(quest=key)

        for obj_record in obj_records:
            objective_type = obj_record.type
            objective = {"ordinal": obj_record.ordinal,
                         "type": objective_type,
                         "object": obj_record.object,
                         "number": obj_record.number,
                         "desc": obj_record.desc}
            self.objectives[obj_record.ordinal] = objective

            accomplished = self.db.accomplished.get(key, 0)
            if accomplished < obj_record.number:
                if not objective_type in self.not_accomplished:
                    self.not_accomplished[objective_type] = [obj_record.ordinal]
                else:
                    self.not_accomplished[objective_type].append(obj_record.ordinal)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if GAME_SETTINGS.get("can_give_up_quests"):
            commands.append({"name": _("Give Up"), "cmd": "giveup_quest", "args": self.get_data_key()})
        return commands

    def return_objectives(self):
        """
        Get the information of all objectives.
        Set desc to an objective can hide the details of the objective.
        """
        objectives = []
        for ordinal in self.objectives:
            desc = self.objectives[ordinal]["desc"]
            if desc:
                # If an objective has desc, use its desc.
                objectives.append({"desc": self.objectives[ordinal]["desc"]})
            else:
                # Or make a desc by other data.
                obj_num = self.objectives[ordinal]["number"]
                accomplished = self.db.accomplished.get(ordinal, 0)
                
                if self.objectives[ordinal]["type"] == defines.OBJECTIVE_TALK:
                    # talking
                    target = _("Talk to")
                    name = DIALOGUE_HANDLER.get_npc_name(self.objectives[ordinal]["object"])
        
                    objectives.append({"target": target,
                                       "object": name,
                                       "accomplished": accomplished,
                                       "total": obj_num,
                                       })
                elif self.objectives[ordinal]["type"] == defines.OBJECTIVE_OBJECT:
                    # getting
                    target = _("Get")
                    name = ""
                    
                    # Get the name of the objective object.
                    object_key = self.objectives[ordinal]["object"]
                    model_names = OBJECT_KEY_HANDLER.get_models(object_key)
                    for model_name in model_names:
                        model = apps.get_model(settings.WORLD_DATA_APP, model_name)
                        # Get record.
                        try:
                            record = model.objects.get(key=object_key)
                            name = record.name
                            break
                        except Exception, e:
                            pass
        
                    objectives.append({"target": target,
                                       "object": name,
                                       "accomplished": accomplished,
                                       "total": obj_num,
                                       })
                elif self.objectives[ordinal]["type"] == defines.OBJECTIVE_KILL:
                    # getting
                    target = _("Kill")
                    name = ""

                    # Get the name of the objective character.
                    object_key = self.objectives[ordinal]["object"]
                    model_names = OBJECT_KEY_HANDLER.get_models(object_key)
                    for model_name in model_names:
                        model = apps.get_model(settings.WORLD_DATA_APP, model_name)
                        # Get record.
                        try:
                            record = model.objects.get(key=object_key)
                            name = record.name
                            break
                        except Exception, e:
                            pass

                    objectives.append({"target": target,
                                       "object": name,
                                       "accomplished": accomplished,
                                       "total": obj_num,
                                       })

        return objectives

    def is_accomplished(self):
        """
        If all objectives are accomplished or not.
        """
        for ordinal in self.objectives:
            obj_num = self.objectives[ordinal]["number"]
            accomplished = self.db.accomplished.get(ordinal, 0)
    
            if accomplished < obj_num:
                return False

        return True

    def complete(self):
        """
        Complete a quest, do its action.
        """
        owner = self.db.owner

        # get rewards
        obj_list = self.loot_handler.get_obj_list(owner)
        if obj_list:
            # give objects to winner
            owner.receive_objects(obj_list)

        # do quest's action
        action = getattr(self.dfield, "action", None)
        if action:
            STATEMENT_HANDLER.do_action(action, owner, None)

        # remove objective objects
        obj_list = []
        for ordinal in self.objectives:
            if self.objectives[ordinal]["type"] == defines.OBJECTIVE_OBJECT:
                obj_list.append({"object": self.objectives[ordinal]["object"],
                                 "number": self.objectives[ordinal]["number"]})
        if obj_list:
            owner.remove_objects(obj_list)

    def at_objective(self, type, object_key, number=1):
        """
        Called when the owner may complete some objectives.
        
        Args:
            type: objective's type defined in defines.py
            object_key: (string) the key of the relative object
            number: (int) the number of the object
        
        Returns:
            if the quest status has changed.
        """
        if type not in self.not_accomplished:
            return False

        status_changed = False
        index = 0

        # search all object objectives
        while index < len(self.not_accomplished[type]):
            ordinal = self.not_accomplished[type][index]
            index += 1

            if self.objectives[ordinal]["object"] == object_key:
                # if this object matches an objective
                status_changed = True

                # add accomplished number
                accomplished = self.db.accomplished.get(ordinal, 0)
                accomplished += number
                self.db.accomplished[ordinal] = accomplished

                if self.db.accomplished[ordinal] >= self.objectives[ordinal]["number"]:
                    # if this objectives is accomplished, remove it
                    index -= 1
                    del(self.not_accomplished[type][index])
                                                                    
                    if not self.not_accomplished[type]:
                        # if all objectives are accomplished
                        del(self.not_accomplished[type])
                        break
                                                                                
        return status_changed
