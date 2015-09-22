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
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from evennia.utils.utils import lazy_property
from evennia import TICKER_HANDLER


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
        print "TICKER_HANDLER remove: %s" % self.name
        TICKER_HANDLER.remove(self)
        return True


    def load_data(self):
        """
        Set data_info to the object."
        """
        # set default values
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
            print "Can't load character level info %s: %s" % (self.db.level, e)


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
            skill_records = model_skills.objects.filter(character=self.get_info_key)

        for skill_record in skill_records:
            self.learn_skill(skill_record.skill_id)

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
        args:
        skill: (string) The key of the skill.
        """
        if skill in self.db.skills:
            self.msg({"alert":LS("You have already learned this skill.")})
            return
                
        skill_obj = build_object(skill)
        if not skill_obj:
            self.msg({"alert":LS("Can not learn this skill.")})
            return
                                
        self.db.skills[skill] = skill_obj
        skill_obj.set_owner(self)


    def has_skill(self, skill):
        """
        Whether the character has the skill.
        args:
            skill: (string) The key of the skill.
        """
        return skill in self.db.skills


    def cast_skill(self, skill, target):
        """
        Cast a skill.
        """
        if not skill in self.db.skills:
            self.msg({"alert":LS("You do not have this skill.")})
            return

        return self.db.skills[skill].cast_skill(target)


    def cast_battle_skill(self, skill, target):
        """
        Cast a skill in battle.
        """
        print "cast_battle_skill: %s" % self.name
        if self.db.GLOBAL_COOLING_DOWN:
            self.msg({"msg":LS("This skill is not ready yet!")})
            return

        if self.db.skills[skill].is_cooling_down():
            self.msg({"msg":LS("This skill is not ready yet!")})
            return
    
        if self.ndb.combat_handler.cast_skill(skill, self.dbref, target):
            # set global cd
            if settings.GLOBAL_CD > 0:
                self.db.GLOBAL_COOLING_DOWN = True
                TICKER_HANDLER.add(self, settings.GLOBAL_CD, hook_key="skill_cooled_down")


    def skill_cooled_down(self):
        """
        """
        print "global_cooled_down"
        del self.db.GLOBAL_COOLING_DOWN
        
        TICKER_HANDLER.remove(self)

        print 1
        # auto cast next skill
        auto_battle_skill = getattr(self, "auto_battle_skill", False)
        if not auto_battle_skill:
            return

        print 2
        if not self.ndb.combat_handler:
            return

        print 3
        if not self.skill_target:
            self.skill_target = self.find_skill_target()
        elif not self.skill_target.is_alive():
            self.skill_target = self.find_skill_target()

        print 4
        if not self.skill_target:
            return

        print 5
        available_skill = self.get_available_skills()
        if not available_skill:
            return

        print 6
        skill = random.choice(available_skill)
        if not skill:
            return

        print 7
        self.cast_battle_skill(skill, self.skill_target.dbref)


    def get_available_skills(self):
        """
        """
        skills = [skill for skill in self.db.skills if not self.db.skills[skill].is_cooling_down()]
        return skills


    def find_skill_target(self):
        """
        """
        if not self.ndb.combat_handler:
            return

        target = None
        characters = self.ndb.combat_handler.get_all_characters()
        for character in characters:
            if character.is_alive() and character.dbref != self.dbref:
                target = character
                break;

        return target


    def start_auto_battle_skill(self):
        """
        """
        print "start_auto_battle_skill: %s" % self.name
        
        # select target
        self.skill_target = self.find_skill_target()
        if not self.skill_target:
            print "if not self.skill_target: %s" % self.name
            return

        self.auto_battle_skill = True

        if self.db.GLOBAL_COOLING_DOWN:
            print "self.db.GLOBAL_COOLING_DOWN: %s" % self.name
            return

        available_skill = self.get_available_skills()
        if not available_skill:
            print "not available_skill: %s" % self.name
            return
        
        skill = random.choice(available_skill)
        if not skill:
            print "not skill: %s" % self.name
            return
        
        self.cast_battle_skill(skill, self.skill_target.dbref)


    def stop_auto_battle_skill(self):
        """
        """
        print "stop_auto_battle_skill"
        self.auto_battle_skill = False


    def is_in_combat(self):
        """
        """
        return bool(self.ndb.combat_handler)


    def hurt(self, damage):
        """
        """
        self.db.hp -= damage
        if self.db.hp < 0:
            self.db.hp = 0

        return


    def die(self):
        """
        """
        pass


    def is_alive(self):
        """
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
