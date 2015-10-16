"""
QuestHandler handles a character's quests.
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
    Handles a character's quests.
    """
    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = owner
        self.current_quests = owner.db.current_quests
        self.finished_quests = owner.db.finished_quests


    def accept(self, quest):
        """
        Accept a quest.
        """
        if quest in self.current_quests:
            return

        # Create quest object.
        new_quest = build_object(quest)
        if not new_quest:
            return

        new_quest.set_owner(self.owner)
        self.current_quests[quest] = new_quest

        self.owner.msg({"msg": LS("Accepted quest {c%s{n.") % new_quest.get_name()})
        self.show_quests()
        self.owner.show_location()


    def finish(self, quest):
        """
        Finish a quest.
        """
        if not quest in self.current_quests:
            return

        if not self.current_quests[quest].is_achieved:
            return

        # Get quest's name.
        name = self.current_quests[quest].get_name()
        
        # Call finish function in the quest.
        self.current_quests[quest].finish()
        
        # Delete the quest.
        del(self.current_quests[quest])

        self.finished_quests.add(quest)
        
        self.owner.msg({"msg": LS("Quest {c%s{n finished.") % name})
        self.show_quests()
        self.owner.show_location()


    def get_achieved_quests(self):
        """
        Get all quests that their objectives are achieved.
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
        If the character is doing this quest.
        """
        return quest in self.current_quests


    def can_provide(self, quest):
        """
        If can provide this quest to the owner.
        """
        if self.owner.quest.is_finished(quest):
            return False

        if self.owner.quest.is_in_progress(quest):
            return False

        if not self.owner.quest.match_dependences(quest):
            return False

        return True


    def match_dependences(self, quest):
        """
        check quest's dependences
        """
        return QUEST_DEP_HANDLER.match_quest_dependences(self.owner, quest)


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
        Called when the owner finishes a dialogue.
        Call relative hooks.
        """
        status_changed = False
        for key in self.current_quests:
            if self.current_quests[key].at_talk_finished(dialogue):
                status_changed = True

        if status_changed:
            self.show_quests()


    def at_get_object(self, obj_key, number):
        """
        Called when the owner gets an object.
        Call relative hooks.
        """
        status_changed = False
        for key in self.current_quests:
            if self.current_quests[key].at_get_object(obj_key, number):
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
