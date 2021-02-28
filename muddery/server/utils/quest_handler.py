"""
QuestHandler handles a character's quests.
"""

import weakref
from evennia.utils import logger
from muddery.server.utils.builder import build_object
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.quest_dependencies import QuestDependencies
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.element_set import ELEMENT


class QuestHandler(object):
    """
    Handles a character's quests.
    """

    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = weakref.proxy(owner)

    def accept(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        current_quests = self.owner.states.load("current_quests", {})
        if quest_key in current_quests:
            return

        # Create quest object.
        new_quest = build_object(quest_key)
        if not new_quest:
            return

        current_quests[quest_key] = new_quest
        self.owner.states.save("current_quests", current_quests)

        self.owner.msg({"msg": _("Accepted quest {C%s{n.") % new_quest.get_name()})
        self.show_quests()
        self.owner.show_location()
        
    def remove_all(self):
        """
        Remove all quests.
        
        It will be called when quests' owner will be deleted.
        """
        current_quests = self.owner.states.load("current_quests", {})
        for quest_key in current_quests:
            current_quests[quest_key].delete()
        self.owner.states.save("current_quests", {})

    def give_up(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not GAME_SETTINGS.get("can_give_up_quests"):
            logger.log_tracemsg("Can not give up quests.")
            raise MudderyError(_("Can not give up this quest."))

        current_quests = self.owner.states.load("current_quests", {})
        if quest_key not in current_quests:
            raise MudderyError(_("Can not find this quest."))

        current_quests[quest_key].delete()
        del(current_quests[quest_key])
        self.owner.states.save("current_quests", current_quests)

        finished_quests = self.owner.states.load("finished_quests", {})
        if quest_key in finished_quests:
            finished_quests.remove(quest_key)
            self.owner.states.save("finished_quests", finished_quests)

        self.show_quests()

    def turn_in(self, quest_key):
        """
        Turn in a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        current_quests = self.owner.states.load("current_quests", {})
        if quest_key not in current_quests:
            return

        if not current_quests[quest_key].is_accomplished:
            return

        # Get quest's name.
        name = current_quests[quest_key].get_name()

        # Call turn in function in the quest.
        current_quests[quest_key].turn_in(self.owner)

        # Delete the quest.
        current_quests[quest_key].delete()
        del (current_quests[quest_key])
        self.owner.states.save("current_quests", current_quests)

        finished_quests = self.owner.states.load("finished_quests", set())
        finished_quests.add(quest_key)
        self.owner.states.save("finished_quests", finished_quests)

        self.owner.msg({"msg": _("Turned in quest {C%s{n.") % name})
        self.show_quests()
        self.owner.show_status()
        self.owner.show_location()

    def get_accomplished_quests(self):
        """
        Get all quests that their objectives are accomplished.
        """
        quests = set()
        current_quests = self.owner.states.load("current_quests", {})
        for quest in current_quests:
            if current_quests[quest].is_accomplished():
                quests.add(quest)

        return quests

    def is_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        current_quests = self.owner.states.load("current_quests", {})
        if quest_key not in current_quests:
            return False

        return current_quests[quest_key].is_accomplished()

    def is_not_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        current_quests = self.owner.states.load("current_quests", {})
        if quest_key not in current_quests:
            return False
        return not current_quests[quest_key].is_accomplished()

    def is_finished(self, quest_key):
        """
        Whether the character finished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        finished_quests = self.owner.states.load("finished_quests", set())
        return quest_key in finished_quests

    def is_in_progress(self, quest_key):
        """
        If the character is doing this quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        current_quests = self.owner.states.load("current_quests", {})
        return quest_key in current_quests

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
            logger.log_errmsg("Can't get quest %s's condition: %s" % (quest_key, e))
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
        quests = []
        current_quests = self.owner.states.load("current_quests", {})
        for quest in current_quests.values():
            info = {"dbref": quest.dbref,
                    "name": quest.name,
                    "desc": quest.get_desc(self.owner),
                    "objectives": quest.return_objectives(),
                    "accomplished": quest.is_accomplished()}
            quests.append(info)

        return quests

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
        current_quests = self.owner.states.load("current_quests", {})
        for quest in current_quests.values():
            if quest.at_objective(object_type, object_key, number):
                status_changed = True
                if quest.is_accomplished():
                    self.owner.msg({"msg":
                        _("Quest {C%s{n's goals are accomplished.") % quest.name})

        if status_changed:
            self.show_quests()
