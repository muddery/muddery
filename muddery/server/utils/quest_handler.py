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


class QuestHandler(object):
    """
    Handles a character's quests.
    """

    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = weakref.proxy(owner)
        self.load_quests()

    def load_quests(self):
        """
        Load character's quests.
        :return:
        """
        self.quests = CharacterQuests.get_character(self.owner.get_db_id())
        for key in self.quests:
            if not self.quests[key]["finished"]:
                self.create_quest(key)

    def accept(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        if quest_key in all_quests:
            return

        # Create quest object.
        quest = self.create_quest(quest_key)
        CharacterQuests.add(self.owner.get_db_id(), quest_key)

        self.owner.msg({"msg": _("Accepted quest {C%s{n.") % quest.get_name()})
        self.show_quests()
        self.owner.show_location()
        
    def remove_all(self):
        """
        Remove all quests.
        
        It will be called when quests' owner will be deleted.
        """
        self.quests = {}
        CharacterQuests.remove_character(self.owner.get_db_id())

    def give_up(self, quest_key):
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

        quest = CharacterQuests.get_quest(self.owner.get_db_id(), quest_key)
        if not quest or quest["finished"]:
            raise MudderyError("Can not find this quest.")

        CharacterQuests.remove_quest(self.owner.get_db_id(), quest_key)
        if quest_key in self.quests:
            del self.quests[quest_key]

        self.show_quests()

    def turn_in(self, quest_key):
        """
        Turn in a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        quest_info = CharacterQuests.get_quest(self.owner.get_db_id(), quest_key)
        if not quest_info or quest_info["finished"]:
            raise MudderyError("Can not find this quest.")

        quest = self.get_quest(quest_key)
        if not quest.is_accomplished():
            raise MudderyError(_("Can not turn in this quest."))

        # Call turn in function in the quest.
        quest.turn_in(self.owner)
        CharacterQuests.set(self.owner.get_db_id(), quest_key, {"finished": True})

        # Get quest's name.
        name = quest.get_name()

        self.owner.msg({"msg": _("Turned in quest {C%s{n.") % name})
        self.show_quests()
        self.owner.show_status()
        self.owner.show_location()

    def is_accomplished(self, quest_key):
        """
        All objectives of this quest are accomplished.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not self.is_in_progress(quest_key):
            return False

        return self.quests[quest_key]["obj"].is_accomplished()

    def is_not_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not self.is_in_progress(quest_key):
            return False

        return not self.quests[quest_key]["obj"].is_accomplished()

    def is_finished(self, quest_key):
        """
        Whether the character finished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        if quest_key not in all_quests:
            return False

        return all_quests[quest_key]["finished"]

    def is_in_progress(self, quest_key):
        """
        If the character is doing this quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        if quest_key not in all_quests:
            return False

        if all_quests[quest_key]["finished"]:
            return False

        return True

    def can_provide(self, quest_key):
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

        if not self.match_dependencies(quest_key):
            return False

        if not self.match_condition(quest_key):
            return False

        return True

    def match_dependencies(self, quest_key):
        """
        Check quest's dependencies

        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        for dep in QuestDependencies.get(quest_key):
            status = QUEST_STATUS_SET.get(dep.type)
            if not status.match(self.owner, dep.dependency):
                return False
        return True

    def match_condition(self, quest_key):
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
            return STATEMENT_HANDLER.match_condition(record.condition, self.owner, None)
        except Exception as e:
            logger.log_err("Can't get quest %s's condition: %s" % (quest_key, e))
        return False

    def show_quests(self):
        """
        Send quests to player.
        """
        quests = self.return_quests()
        self.owner.msg({"quests": quests})

    def return_quests(self):
        """
        Get quests' data.
        """
        quests_info = []

        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        for quest_key, info in all_quests.items():
            if info["finished"]:
                continue

            quest = self.get_quest(quest_key)
            quests_info.append(quest.return_info())

        return quests_info

    def at_objective(self, object_type, object_key, number=1):
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
        status_changed = False
        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        for quest_key, info in all_quests.items():
            if info["finished"]:
                continue

            quest = self.get_quest(quest_key)

            if quest.at_objective(object_type, object_key, number):
                status_changed = True
                if quest.is_accomplished():
                    self.owner.msg({"msg": _("Quest {C%s{n's goals are accomplished.") % quest.get_name()})

        if status_changed:
            self.show_quests()

    def create_quest(self, quest_key):
        """
        Get a quest object by its key.
        :param quest_key:
        :return:
        """
        quest = ELEMENT("QUEST")()
        quest.setup_element(quest_key)
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
        if quest_key in self.quests:
            quest = self.quests[quest_key]["obj"]
        else:
            quest = self.create_quest(quest_key)

        return quest

    def get_quest_info(self, quest_key):
        """
        Get a quest's detail information.
        :param quest_key:
        :return:
        """
        all_quests = CharacterQuests.get_character(self.owner.get_db_id())
        if all_quests[quest_key]["finished"]:
            logger.log_err("%s's quest %s is finished." % (self.owner.get_db_id(), quest_key))
            return

        quest = self.get_quest(quest_key)
        return quest.return_info()
