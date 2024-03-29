"""
Quests

The quest class represents the character's quest. Each quest is a quest object stored
in the character. It controls quest's objectives.

"""

from muddery.server.utils.logger import logger
from muddery.common.utils import defines
from muddery.server.database.gamedata.character_quest_objectives import CharacterQuestObjectives
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GameSettings
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.loot_list import QuestRewardList
from muddery.server.database.worlddata.quest_objectives import QuestObjectives
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.elements.base_element import BaseElement
from muddery.common.utils.utils import async_gather, async_wait


class MudderyQuest(BaseElement):
    """
    This class controls quest's objectives. Hooks are called when a character doing some things.
    """
    element_type = "QUEST"
    element_name = "Quest"
    model_name = "quests"

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyQuest, self).__init__()

        self.loot_handler = None

    async def at_element_setup(self, first_time):
        """
        Set data_info to the object.
        """
        await super(MudderyQuest, self).at_element_setup(first_time)

        # initialize loot handler
        self.loot_handler = LootHandler(QuestRewardList.get(self.get_element_key()))

    def set_character(self, character_id):
        """
        Load a character's quest's data from db.
        """
        self.character_id = character_id
        self.objectives = {}

        # Get objectives.
        records = QuestObjectives.get(self.get_element_key())

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

    async def get_info(self):
        """
        Get return messages for the client.
        """
        # Get name, description and available commands.
        cmds, objectives = await async_gather([
            self.get_available_commands(),
            self.get_objectives(),
        ])
        info = {
            "key": self.const.key,
            "name": self.const.name,
            "desc": self.const.desc,
            "cmds": cmds,
            "icon": getattr(self, "icon", None),
            "objectives": objectives,
        }
        return info

    async def get_available_commands(self):
        """
        This returns a list of available commands.
        """
        commands = []
        if GameSettings.inst().get("can_give_up_quests"):
            commands.append({
                "name": _("Give Up"),
                "cmd": "give_up_quest",
                "args": self.const.key,
                "confirm": _("Give up this quest?"),
            })
        return commands

    def get_objective_types(self):
        """
        Get objective's type and objective's key.
        :return:
        """
        return self.objectives.keys()

    async def get_objectives(self):
        """
        Get the information of all objectives.
        Set desc to an objective can hide the details of the objective.
        """
        output = []
        all_objectives = await CharacterQuestObjectives.inst().get_character_quest(
            self.character_id,
            self.get_element_key()
        )

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
                accomplished = all_objectives.get(character_quest)
                accomplished = accomplished if accomplished else 0
                
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

    async def is_accomplished(self):
        """
        All objectives of this quest are accomplished.
        """
        all_objectives = await CharacterQuestObjectives.inst().get_character_quest(
            self.character_id,
            self.get_element_key()
        )

        for item in self.objectives.values():
            character_quest = "%s:%s" % (item["type"], item["object"])
            accomplished = all_objectives.get(character_quest)
            accomplished = accomplished if accomplished else 0
            if accomplished < item["number"]:
                return False

        return True

    async def turn_in(self, caller):
        """
        Turn in a quest, do its action.
        """
        if not caller:
            return

        # get rewards
        receive_list = await self.loot_handler.get_obj_list(caller)

        awaits = []
        if receive_list:
            # give objects to winner
            awaits.append(caller.receive_objects(receive_list))

        # get exp
        exp = self.const.exp
        if exp:
            awaits.append(caller.add_exp(exp))

        # do quest's action
        action = self.const.action
        if action:
            awaits.append(STATEMENT_HANDLER.do_action(action, caller, None))

        # remove objective objects
        remove_list = []
        for item in self.objectives.values():
            if item["type"] == defines.OBJECTIVE_OBJECT:
                remove_list.append({
                    "object_key": item["object"],
                    "number": item["number"]
                })
        if remove_list:
            await caller.remove_objects_by_list(remove_list)

        if awaits:
            await async_wait(awaits)

        # remove quest objectives records
        await CharacterQuestObjectives.inst().remove(
            self.character_id,
            self.const.key
        )

    async def at_objective(self, objective_type, object_key, number=1):
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

        accomplished = await CharacterQuestObjectives.inst().get_progress(
            self.character_id,
            self.get_element_key(),
            item["type"],
            item["object"],
            0
        )

        if accomplished == item["number"]:
            # already accomplished
            return False

        accomplished += number
        if accomplished > item["number"]:
            accomplished = item["number"]

        await CharacterQuestObjectives.inst().save_progress(
            self.character_id,
            self.get_element_key(),
            objective_type,
            object_key,
            accomplished
        )

        return True

