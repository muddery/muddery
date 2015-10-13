"""
QuestHandler
"""

import re
from muddery.utils import defines
from muddery.utils.builder import build_object
from muddery.utils.quest_dependency_handler import QUEST_DEP_HANDLER
from muddery.utils.localized_strings_handler import LS
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class QuestHandler(object):
    """
    """
    def __init__(self, character):
        """
        Initialize handler
        """
        self.character = character
        self.current_quests = self.character.db.current_quests
        self.finished_quests = self.character.db.finished_quests


    def accept(self, quest):
        """
        Accept a quest.
        """
        if quest in self.current_quests:
            return

        new_quest = build_object(quest)
        if not new_quest:
            return

        self.current_quests[quest] = new_quest
        self.character.msg({"msg": LS("Accepted quest {c%s{n.") % new_quest.get_name()})
        self.show_quests()
        self.character.show_location()


    def finish(self, quest):
        """
        Finish a quest.
        """
        if not quest in self.current_quests:
            return

        if not self.current_quests[quest].is_achieved:
            return

        self.current_quests[quest].finish()
        del(self.current_quests[quest])
        self.finished_quests.add(quest)
        self.show_quests()
        self.character.show_location()


    def get_achieved_quests(self):
        """
        """
        quests = set()
        for quest in self.current_quests:
            if self.current_quests[quest].is_achieved():
                quests.add(quest)

        return quests


    def is_finished(self, quest):
        """
        Whether the character finished this quest.
        """
        return quest in self.finished_quests


    def is_in_progress(self, quest):
        """
        Whether the character is doing this quest.
        """
        return quest in self.current_quests


    def can_provide(self, quest):
        """
        """
        if self.character.quest.is_finished(quest):
            return False

        if self.character.quest.is_in_progress(quest):
            return False

        if not self.character.quest.match_dependences(quest):
            return False

        return True


    def match_dependences(self, quest):
        """
        check quest's dependences
        """
        return QUEST_DEP_HANDLER.match_quest_dependences(self.character, quest)


    def show_quests(self):
        """
        Send quests to player.
        """
        quests = self.return_quests()
        self.character.msg({"quests": quests})


    def return_quests(self):
        """
        Get quests' data.
        """
        quests = []
        for key in self.current_quests:
            quest = self.current_quests[key]
            info = {"dbref": quest.dbref,
                    "name": quest.name,
                    "desc": quest.db.desc,
                    "objectives": quest.return_objectives()}
            quests.append(info)

        return quests


    def at_talk_finished(self, dialogue):
        """
        """
        status_changed = False
        for key in self.current_quests:
            if self.current_quests[key].at_talk_finished(dialogue):
                status_changed = True

        if status_changed:
            self.show_quests()


    def at_character_move_in(self, location):
        """
        """
        pass


    def at_character_move_out(self):
        """
        """
        pass
