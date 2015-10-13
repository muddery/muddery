"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import traceback
import random
from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.objects import MudderyObject
from muddery.typeclasses.common_objects import MudderyEquipment
from evennia.objects.objects import DefaultCharacter
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from muddery.utils.skill_handler import SkillHandler


class MudderyCharacter(MudderyObject, DefaultCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """

    # initialize all handlers in a lazy fashion
    @lazy_property
    def skill(self):
        return SkillHandler(self)


    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()
        
        self.db.level = 1
        self.db.exp = 0
        self.db.hp = 1
        self.db.mp = 1
        self.db.team = 0

        equipments = {}
        for position in settings.EQUIP_POSITIONS:
            equipments[position] = None
        self.db.equipments = equipments
        
        self.db.skills = {}
        
        # set quests
        self.db.finished_quests = set()
        self.db.current_quests = {}


    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.

        """
        super(MudderyCharacter, self).at_object_delete()

        if self.db.GLOBAL_COOLING_DOWN or self.db.AUTO_BATTLE_SKILL:
            TICKER_HANDLER.remove(self)

        return True


    def load_data(self):
        """
        Set data_info to the object."
        """
        # set default values
        self.max_exp = 1
        self.max_hp = 1
        self.max_mp = 1
        
        self.attack = 0
        self.defence = 0
        
        self.skill_cd = 0
        
        super(MudderyCharacter, self).load_data()
        
        self.refresh_data()


    def set_level(self, level):
        """
        Set character's level.
        """
        if self.db.level == level:
            return

        self.db.level = level
        self.refresh_data()


    def refresh_data(self):
        """
        Refresh character's data, calculate character's attributes.
        """
        # load level data
        self.load_level_data()
        
        # load equips data
        self.load_equip_data()


    def load_level_data(self):
        """
        Load character's level data.
        """
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.CHARACTER_LEVELS)
            level_data = model_obj.objects.get(character=self.get_info_key(), level=self.db.level)

            known_fields = set(["id",
                                "character",
                                "level"])
            for field in level_data._meta.fields:
                if field.name in known_fields:
                    continue
                if field.name in self.reserved_fields:
                    print "Can not set reserved field %s!" % field.name
                    continue
                setattr(self, field.name, level_data.serializable_value(field.name))
        except Exception, e:
            print "Can't load character %s's level info %s: %s" % (self.get_info_key(), self.db.level, e)


    def set_equips(self):
        """
        Load equipments data.
        """
        # set equipments status
        equipped = set()
        equipments = self.db.equipments
        for position in equipments:
            if equipments[position]:
                equipped.add(equipments[position])

        for content in self.contents:
            if content.dbref in equipped:
                content.equipped = True

        # set character's attributes
        self.refresh_data()


    def load_equip_data(self):
        """
        """
        # find equipments
        equipped = set([equip_id for equip_id in self.db.equipments.values() if equip_id])

        # add equipment's attributes
        for content in self.contents:
            if content.dbref in equipped:
                for effect in settings.EQUIP_EFFECTS:
                    value = getattr(self, effect, 0)
                    value += getattr(content, effect, 0)
                    setattr(self, effect, value)


    def set_initial_data(self):
        """
        Initialize this object after data loaded.
        """
        super(MudderyCharacter, self).set_initial_data()
        
        # default skills
        skill_records = []
        model_skills = get_model(settings.WORLD_DATA_APP, settings.CHARACTER_SKILLS)
        if model_skills:
            # Get records.
            skill_records = model_skills.objects.filter(character=self.get_info_key())

        for skill_record in skill_records:
            self.skill.learn_skill(skill_record.skill_id)

        # set initial data
        self.db.hp = self.max_hp


    def use_object(self, obj):
        """
        Use an object.
        """
        pass


    def learn_skill(self, skill):
        """
        Learn a new skill.
        """
        self.skill.learn_skill(skill)


    def has_skill(self, skill):
        """
        Whether the character has the skill.
        """
        self.skill.has_skill(skill)


    def cast_skill(self, skill, target):
        """
        Cast a skill.
        """
        self.skill.cast_skill(skill, target)


    def is_in_combat(self):
        """
        If is in combat.
        """
        return bool(self.ndb.combat_handler)


    def set_team(self, team_id):
        """
        Set character's team id in combat.
        """
        self.db.team = team_id


    def get_team(self):
        """
        Get character's team id in combat.
        """
        return self.db.team


    def hurt(self, damage):
        """
        Be hurted.
        """
        self.db.hp -= damage
        if self.db.hp < 0:
            self.db.hp = 0

        return


    def die(self, killers):
        """
        This character die.
        """
        # trigger event
        self.event.at_character_die(self, killers)


    def is_alive(self):
        """
        If this character is alive.
        """
        return self.db.hp > 0


    def get_combat_commands(self):
        """
        This returns a list of combat commands.
        """
        commands = []
        for key in self.db.skills:
            skill = self.db.skills[key]
            command = {"name": skill.name,
                       "key": skill.get_info_key()}
            commands.append(command)
        return commands
