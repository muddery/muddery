"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from muddery.server.utils.logger import game_server_logger as logger
from muddery.server.utils import defines
from muddery.server.database.gamedata.quest_objectives import QuestObjectives
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.loot_list import QuestRewardList
from muddery.server.database.worlddata.quest_objectives import QuestObjectives
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.elements.base_element import BaseElement


class MudderyQuest(BaseElement):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_type = "QUEST"
    element_name = _("Quest", "elements")
    model_name = "quests"

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyQuest, self).__init__()

        self.loot_handler = None

    def at_element_setup(self, first_time):
        """
        Set data_info to the object.
        """
        super(MudderyQuest, self).at_element_setup(first_time)

        # initialize loot handler
        self.loot_handler = LootHandler(QuestRewardList.get(self.get_element_key()))

    def set_character(self, character_id):
        """
        Load a character's quest's data from db.
        """
        self.character_id = character_id
        self.objectives = {}

        if not self.element_key:
            return

        # Get objectives.
        records = QuestObjectives.get(self.element_key)

        for record in records:
            self.objectives[(record.type, record.object)] = {
                "type": record.type,
                "object": record.object,
                "number": record.number,
                "desc": record.desc,
            }

    def get_name(self):
        """
        Get the quest's name.
        :return:
        """
        return self.const.name

    def return_info(self):
        """
        Get return messages for the client.
        """
        # Get name, description and available commands.
        info = {
            "key": self.const.key,
            "name": self.const.name,
            "desc": self.const.desc,
            "cmds": self.get_available_commands(),
            "icon": getattr(self, "icon", None),
            "objectives": self.return_objectives(),
        }
        return info

    def get_available_commands(self):
        """
        This returns a list of available commands.
        """
        commands = []
        if GAME_SETTINGS.get("can_give_up_quests"):
            commands.append({"name": _("Give Up"), "cmd": "giveup_quest", "args": self.const.key})
        return commands

    def return_objectives(self):
        """
        Get the information of all objectives.
        Set desc to an objective can hide the details of the objective.
        """
        output = []
        all_accomplished = QuestObjectives.get_character_quest(self.character_id, self.element_key)

        for item in self.objectives.values():
            desc = item["desc"]
            if desc:
                # If an objective has desc, use its desc.
                output.append({
                    "desc": item["desc"]
                })
            else:
                # Or make a desc by other data.
                obj_num = item["number"]
                character_quest = "%s:%s" % (item["type"], item["object"])
                accomplished = all_accomplished.get(character_quest, 0)
                
                if item["type"] == defines.OBJECTIVE_TALK:
                    # talk to a character
                    target = _("Talk to")
                    name = ""

                    # Get the name of the objective character.
                    object_key = item["object"]
                    model_name = ELEMENT("CHARACTER").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
        
                    output.append({
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })

                elif item["type"] == defines.OBJECTIVE_OBJECT:
                    # get objects
                    target = _("Get")
                    
                    # Get the name of the objective object.
                    object_key = item["object"]
                    model_name = ELEMENT("COMMON_OBJECT").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
                        continue
        
                    output.append({
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })

                elif item["type"] == defines.OBJECTIVE_KILL:
                    # kill someone
                    target = _("Kill")

                    # Get the name of the objective character.
                    object_key = item["object"]
                    model_name = ELEMENT("CHARACTER").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
                        continue

                    output.append({
                        "target": target,
                        "object": name,
                        "accomplished": accomplished,
                        "total": obj_num,
                    })
                elif item["type"] == defines.OBJECTIVE_ARRIVE:
                    # arrive some place
                    target = _("Arrive")

                    # Get the name of the objective character.
                    object_key = item["object"]
                    model_name = ELEMENT("ROOM").model_name

                    # Get record.
                    try:
                        record = WorldData.get_table_data(model_name, key=object_key)
                        record = record[0]
                        name = record.name
                    except Exception as e:
                        logger.log_err("Can not find the quest object: %s" % object_key)
                        continue

                    output.append({
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
        all_accomplished = QuestObjectives.get_character_quest(self.character_id, self.element_key)

        for item in self.objectives.values():
            character_quest = "%s:%s" % (item["type"], item["object"])
            accomplished = all_accomplished.get(character_quest, 0)
            if accomplished < item["number"]:
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
        exp = self.const.exp
        if exp:
            caller.add_exp(exp)

        # do quest's action
        action = self.const.action
        if action:
            STATEMENT_HANDLER.do_action(action, caller, None)

        # remove objective objects
        obj_list = []
        for item in self.objectives.values():
            if item["type"] == defines.OBJECTIVE_OBJECT:
                obj_list.append({
                    "object_key": item["object"],
                    "number": item["number"]
                })
        if obj_list:
            caller.remove_objects_by_list(obj_list)

        # remove quest objectives records
        QuestObjectives.remove(self.character_id, self.const.key)

    def at_objective(self, objective_type, object_key, number=1):
        """
        Called when the owner may complete some objectives.
        
        Args:
            objective_type: objective's type defined in defines.py
            object_key: (string) the key of the relative object
            number: (int) the number of the object
        
        Returns:
            if the quest status has changed.
        """
        if (objective_type, object_key) not in self.objectives:
            return False

        item = self.objectives[(objective_type, object_key)]

        accomplished = QuestObjectives.get_progress(self.character_id, self.element_key, item["type"],
                                                    item["object"], 0)

        if accomplished == item["number"]:
            # already accomplished
            return False

        accomplished += number
        if accomplished > item["number"]:
            accomplished = item["number"]

        QuestObjectives.save_progress(self.character_id, self.element_key, objective_type, object_key, accomplished)

        return True

