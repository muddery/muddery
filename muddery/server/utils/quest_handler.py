"""
QuestHandler handles a character's quests.
"""

import weakref
from muddery.server.utils.logger import logger
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.game_settings import GameSettings
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.quest_dependencies import QuestDependencies
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.gamedata.character_quests import CharacterQuests
from muddery.server.database.gamedata.character_finished_quests import CharacterFinishedQuests
from muddery.server.utils.utils import async_wait, async_gather


class QuestHandler(object):
    """
    Handles a character's quests.
    """

    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = weakref.proxy(owner)
        self.quests = {}
        self.finished_quests = set()

        self.objectives = {}

    async def init(self):
        """
        Initial setup.
        """
        await self.load_quests()

    async def load_quests(self):
        """
        Load character's quests.
        :return:
        """
        quest_keys = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if quest_keys:
            await async_wait([self.create_quest(key) for key in quest_keys])

        finished_quests = await CharacterFinishedQuests.inst().get_character(self.owner.get_db_id())
        self.finished_quests = set(finished_quests.keys())

        self.calculate_objectives()

    async def accept(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if quest_key in self.quests or quest_key in self.finished_quests:
            return

        # Create quest object.
        quest = await self.create_quest(quest_key)
        await CharacterQuests.inst().add(self.owner.get_db_id(), quest_key)
        self.add_objectives(quest)

        await self.owner.msg({"msg": _("Accepted quest {C%s{n.") % quest.get_name()})
        await self.show_quests()
        await self.owner.show_location()
        
    async def remove_all(self):
        """
        Remove all quests.
        
        It will be called when quests' owner will be deleted.
        """
        self.quests = {}
        self.finished_quests = set()
        self.objectives = {}
        await async_wait([
            CharacterQuests.inst().remove_character(self.owner.get_db_id()),
            CharacterFinishedQuests.inst().remove_character(self.owner.get_db_id()),
        ])

    async def give_up(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not GameSettings.inst().get("can_give_up_quests"):
            logger.log_trace("Can not give up quests.")
            raise MudderyError(_("Can not give up this quest."))

        if quest_key not in self.quests:
            raise MudderyError("Can not find this quest.")

        await CharacterQuests.inst().remove_quest(self.owner.get_db_id(), quest_key)
        del self.quests[quest_key]
        self.calculate_objectives()

        await self.show_quests()

    async def turn_in(self, quest_key):
        """
        Turn in a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if quest_key not in self.quests:
            raise MudderyError("Can not find this quest.")

        quest = self.get_quest(quest_key)
        if not await quest.is_accomplished():
            raise MudderyError(_("Can not turn in this quest."))

        # Get quest's name.
        name = quest.get_name()

        # Call turn in function in the quest.
        await quest.turn_in(self.owner)
        await CharacterFinishedQuests.inst().add(self.owner.get_db_id(), quest_key)
        await CharacterQuests.inst().remove(self.owner.get_db_id(), quest_key)
        self.finished_quests.add(quest_key)
        del self.quests[quest_key]
        self.calculate_objectives()

        await self.owner.msg({"msg": _("Turned in quest {C%s{n.") % name})
        await self.show_quests()
        await self.owner.show_status()
        await self.owner.show_location()

    async def is_accomplished(self, quest_key):
        """
        All objectives of this quest are accomplished.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not self.is_in_progress(quest_key):
            return False

        return await self.quests[quest_key]["obj"].is_accomplished()

    async def is_not_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not self.is_in_progress(quest_key):
            return False

        return not await self.quests[quest_key]["obj"].is_accomplished()

    def is_finished(self, quest_key):
        """
        Whether the character finished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        return quest_key in self.finished_quests

    def is_in_progress(self, quest_key):
        """
        If the character is doing this quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        return quest_key in self.quests

    async def can_provide(self, quest_key):
        """
        If can provide this quest to the owner.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if self.is_finished(quest_key):
            return False

        if self.is_in_progress(quest_key):
            return False

        if not await self.match_dependencies(quest_key):
            return False

        if not await self.match_condition(quest_key):
            return False

        return True

    async def match_dependencies(self, quest_key):
        """
        Check quest's dependencies

        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        dependencies = QuestDependencies.get(quest_key)
        if dependencies:
            results = await async_gather([
                QUEST_STATUS_SET.get(dep.type).match(self.owner, dep.dependency) for dep in dependencies
            ])
        else:
            return True

        return min(results)

    async def match_condition(self, quest_key):
        """
        Check if the quest matches its condition.
        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        # Get quest's record.
        model_name = ELEMENT("QUEST").model_name
        if not model_name:
            return False

        try:
            record = WorldData.get_table_data(model_name, key=quest_key)
            record = record[0]
            return await STATEMENT_HANDLER.match_condition(record.condition, self.owner, None)
        except Exception as e:
            logger.log_err("Can't get quest %s's condition: %s" % (quest_key, e))
        return False

    async def show_quests(self):
        """
        Send quests to player.
        """
        quests = await self.get_quests_info()
        await self.owner.msg({"quests": quests})

    async def get_quests_info(self):
        """
        Get quests' data.
        """
        if self.quests:
            quests_info = await async_gather([quest["obj"].return_info() for quest in self.quests.values()])
        else:
            quests_info = []

        return quests_info

    def add_objectives(self, quest):
        key = quest.get_element_key()
        objective_types = quest.get_objective_types()
        for objective_type in objective_types:
            if objective_type not in self.objectives:
                self.objectives[objective_type] = [key]
            else:
                self.objectives[objective_type].append(key)

    def calculate_objectives(self):
        objectives = {}
        for key, quest in self.quests.items():
            objective_types = quest["obj"].get_objective_types()
            for objective_type in objective_types:
                if objective_type not in objectives:
                    objectives[objective_type] = [key]
                else:
                    objectives[objective_type].append(key)

        self.objectives = objectives

    async def at_objective(self, object_type, object_key, number=1):
        """
        Called when the owner may complete some objectives.
        Call relative hooks.

        Args:
            object_type: (type) objective's type
            object_key: (string) object's key
            number: (int) objective's number

        Returns:
            None
        """
        if (object_type, object_key) not in self.objectives:
            return

        status_changed = False

        quest_keys = self.objectives[(object_type, object_key)]
        if quest_keys:
            # Check objectives.
            quests = [self.get_quest(key) for key in quest_keys]
            results = await async_gather([quest.at_objective(object_type, object_key, number) for quest in quests])
            quests = [quest["obj"] for index, quest in enumerate(self.quests.values()) if results[index]]

            if quests:
                status_changed = True

                # Check if quest is accomplished.
                accomplished = await async_gather([quest.is_accomplished() for quest in quests])
                quest_names = [quest.get_name() for index, quest in enumerate(quests) if accomplished[index]]
                
                if quest_names:
                    # Notify the player.
                    await self.owner.msg([
                        {"msg": _("Quest {C%s{n's goals are accomplished.") % n} for n in quest_names
                    ])

        if status_changed:
            await self.show_quests()

    async def create_quest(self, quest_key):
        """
        Get a quest object by its key.
        :param quest_key:
        :return:
        """
        quest = ELEMENT("QUEST")()
        await quest.setup_element(quest_key)
        quest.set_character(self.owner.get_db_id())
        self.quests[quest_key] = {
            "obj": quest
        }

        return quest

    def get_quest(self, quest_key):
        """
        Get a quest object by its key.
        :param quest_key:
        :return:
        """
        return self.quests[quest_key]["obj"]

    async def get_quest_info(self, quest_key):
        """
        Get a quest's detail information.
        :param quest_key:
        :return:
        """
        quest = self.get_quest(quest_key)
        return await quest.return_info()
