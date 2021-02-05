"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.server.utils import defines
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.dao.worlddata import WorldData
from muddery.server.dao.loot_list import QuestLootList
from muddery.server.dao.quest_objectives import QuestObjectives
from muddery.server.mappings.element_set import ELEMENT


class MudderyQuest(ELEMENT("OBJECT")):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_key = "QUEST"
    element_name = _("Quest", "elements")
    model_name = "quests"

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, QuestLootList.get(self.get_data_key()))

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
        obj_records = QuestObjectives.get(key)
        all_accomplished = self.state.load("accomplished", {})

        for obj_record in obj_records:
            objective_type = obj_record.type
            objective = {"ordinal": obj_record.ordinal,
                         "type": objective_type,
                         "object": obj_record.object,
                         "number": obj_record.number,
                         "desc": obj_record.desc}
            self.objectives[obj_record.ordinal] = objective

            accomplished = all_accomplished.get(key, 0)
            if accomplished < obj_record.number:
                if not objective_type in self.not_accomplished:
                    self.not_accomplished[objective_type] = [obj_record.ordinal]
                else:
                    self.not_accomplished[objective_type].append(obj_record.ordinal)

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # Get name, description and available commands.
        info = super(MudderyQuest, self).get_appearance(caller)

        info["objectives"] = self.return_objectives()
        return info

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
        output = []
        all_accomplished = self.state.load("accomplished", {})

        for ordinal, objective in self.objectives.items():
            desc = objective["desc"]
            if desc:
                # If an objective has desc, use its desc.
                output.append({
                    "ordinal": ordinal,
                    "desc": objective["desc"]
                })
            else:
                # Or make a desc by other data.
                obj_num = objective["number"]
                accomplished = all_accomplished.get(ordinal, 0)
                
                if objective["type"] == defines.OBJECTIVE_TALK:
                    # talking
                    target = _("Talk to")
                    name = DIALOGUE_HANDLER.get_npc_name(objective["object"])
        
                    output.append({
                        "ordinal": ordinal,
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })

                elif objective["type"] == defines.OBJECTIVE_OBJECT:
                    # getting
                    target = _("Get")
                    
                    # Get the name of the objective object.
                    object_key = objective["object"]
                    model_name = ELEMENT("OBJECT").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
                        continue
        
                    output.append({
                        "ordinal": ordinal,
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })

                elif self.objectives[ordinal]["type"] == defines.OBJECTIVE_KILL:
                    # getting
                    target = _("Kill")

                    # Get the name of the objective character.
                    object_key = self.objectives[ordinal]["object"]
                    model_name = ELEMENT("OBJECT").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
                        continue

                    output.append({
                        "ordinal": ordinal,
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })

        return output

    def is_accomplished(self):
        """
        All objectives of this quest are accomplished.
        """
        all_accomplished = self.state.load("accomplished", {})

        for ordinal in self.objectives:
            obj_num = self.objectives[ordinal]["number"]
            accomplished = all_accomplished.get(ordinal, 0)
    
            if accomplished < obj_num:
                return False

        return True

    def turn_in(self, caller):
        """
        Turn in a quest, do its action.
        """
        if not caller:
            return

        # get rewards
        obj_list = self.loot_handler.get_obj_list(caller)
        if obj_list:
            # give objects to winner
            caller.receive_objects(obj_list)

        # get exp
        exp = getattr(self.system, "exp", 0)
        if exp:
            caller.add_exp(exp)

        # do quest's action
        action = getattr(self.system, "action", None)
        if action:
            STATEMENT_HANDLER.do_action(action, caller, None)

        # remove objective objects
        obj_list = []
        for ordinal in self.objectives:
            if self.objectives[ordinal]["type"] == defines.OBJECTIVE_OBJECT:
                obj_list.append({"object": self.objectives[ordinal]["object"],
                                 "number": self.objectives[ordinal]["number"]})
        if obj_list:
            caller.remove_objects(obj_list)

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

        all_accomplished = self.state.load("accomplished", {})
        changed = False

        # search all object objectives
        while index < len(self.not_accomplished[type]):
            ordinal = self.not_accomplished[type][index]
            index += 1

            if self.objectives[ordinal]["object"] == object_key:
                # if this object matches an objective
                status_changed = True

                # add accomplished number
                accomplished = all_accomplished.get(ordinal, 0)
                accomplished += number
                all_accomplished[ordinal] = accomplished
                changed = True

                if all_accomplished[ordinal] >= self.objectives[ordinal]["number"]:
                    # if this objectives is accomplished, remove it
                    index -= 1
                    del(self.not_accomplished[type][index])
                                                                    
                    if not self.not_accomplished[type]:
                        # if all objectives are accomplished
                        del(self.not_accomplished[type])
                        break

        if changed:
            self.state.save("accomplished", all_accomplished)

        return status_changed

