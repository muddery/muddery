"""
QuestHandler handles a character's quests.
"""

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.utils.builder import build_object
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.localized_strings_handler import _
from muddery.utils.exception import MudderyError
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from muddery.utils.game_settings import GAME_SETTINGS


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
        self.completed_quests = owner.db.completed_quests

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

        del(self.current_quests[quest_key])

        self.completed_quests.add(quest_key)
        if quest_key in self.completed_quests:
            self.completed_quests.remove(quest_key)

        self.show_quests()

    def complete(self, quest_key):
        """
        Complete a quest.

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

        # Call complete function in the quest.
        self.current_quests[quest_key].complete()

        # Delete the quest.
        del (self.current_quests[quest_key])

        self.completed_quests.add(quest_key)

        self.owner.msg({"msg": _("Completed quest {c%s{n.") % name})
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

    def is_completed(self, quest_key):
        """
        Whether the character completed this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        return quest_key in self.completed_quests

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
        if self.is_completed(quest_key):
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
        return QUEST_DEP_HANDLER.match_quest_dependencies(self.owner, quest_key)

    def match_condition(self, quest_key):
        """
        Check if the quest matches its condition.
        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        # Get quest's record.
        model_names = OBJECT_KEY_HANDLER.get_models(quest_key)
        if not model_names:
            return False

        for model_name in model_names:
            model_quest = apps.get_model(settings.WORLD_DATA_APP, model_name)

            try:
                record = model_quest.objects.get(key=quest_key)
                return STATEMENT_HANDLER.match_condition(record.condition, self.owner, None)
            except ObjectDoesNotExist:
                continue
            except AttributeError:
                continue

        return True

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
