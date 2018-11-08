"""
QuestHandler handles a character's quests.
"""

from __future__ import print_function

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.utils.builder import build_object
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.localized_strings_handler import _
from muddery.utils.exception import MudderyError
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.dao.quest_dependencies_mapper import QUEST_DEPENDENCIES
from muddery.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.mappings.typeclass_set import TYPECLASS


class QuestHandler(object):
    """
    Handles a character's quests.
    """

    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = owner
        self.current_quests = owner.db.current_quests
        self.finished_quests = owner.db.finished_quests

    def accept(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if quest_key in self.current_quests:
            return

        # Create quest object.
        new_quest = build_object(quest_key)
        if not new_quest:
            return

        new_quest.set_owner(self.owner)
        self.current_quests[quest_key] = new_quest

        self.owner.msg({"msg": _("Accepted quest {c%s{n.") % new_quest.get_name()})
        self.show_quests()
        self.owner.show_location()
        
    def remove_all(self):
        """
        Remove all quests.
        
        It will be called when quests' owner will be deleted.
        """
        for quest_key in self.current_quests:
            self.current_quests[quest_key].delete()
        self.current_quests = []

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

        if quest_key not in self.current_quests:
            raise MudderyError(_("Can not find this quest."))

        self.current_quests[quest_key].delete()
        del(self.current_quests[quest_key])

        if quest_key in self.finished_quests:
            self.finished_quests.remove(quest_key)

        self.show_quests()

    def turn_in(self, quest_key):
        """
        Turn in a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if quest_key not in self.current_quests:
            return

        if not self.current_quests[quest_key].is_accomplished:
            return

        # Get quest's name.
        name = self.current_quests[quest_key].get_name()

        # Call turn in function in the quest.
        self.current_quests[quest_key].turn_in()

        # Delete the quest.
        self.current_quests[quest_key].delete()
        del (self.current_quests[quest_key])

        self.finished_quests.add(quest_key)

        self.owner.msg({"msg": _("Turned in quest {c%s{n.") % name})
        self.show_quests()
        self.owner.show_location()

    def get_accomplished_quests(self):
        """
        Get all quests that their objectives are accomplished.
        """
        quests = set()
        for quest in self.current_quests:
            if self.current_quests[quest].is_accomplished():
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
        if quest_key not in self.current_quests:
            return False

        return self.current_quests[quest_key].is_accomplished()

    def is_not_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if quest_key not in self.current_quests:
            return False
        return not self.current_quests[quest_key].is_accomplished()

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
        return quest_key in self.current_quests

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
        for dep in QUEST_DEPENDENCIES.filter(quest_key):
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
        model_name = TYPECLASS("QUEST").model_name
        if not model_name:
            return False

        model_quest = apps.get_model(settings.WORLD_DATA_APP, model_name)

        try:
            record = model_quest.objects.get(key=quest_key)
            return STATEMENT_HANDLER.match_condition(record.condition, self.owner, None)
        except Exception, e:
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
        for quest in self.current_quests.values():
            info = {"dbref": quest.dbref,
                    "name": quest.name,
                    "desc": quest.db.desc,
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
        for quest in self.current_quests.values():
            if quest.at_objective(object_type, object_key, number):
                status_changed = True
                if quest.is_accomplished():
                    self.owner.msg({"msg":
                        _("Quest {c%s{n's goals are accomplished.") % quest.name})

        if status_changed:
            self.show_quests()
