"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

import time, traceback
from twisted.internet import reactor, task
from twisted.internet.task import deferLater
from django.conf import settings
from evennia.objects.objects import DefaultCharacter
from evennia import create_script
from evennia.typeclasses.models import DbHolder
from evennia.utils import logger
from evennia.utils.utils import lazy_property, class_from_module
from muddery.typeclasses.objects import MudderyObject
from muddery.mappings.typeclass_set import typeclass_mapping, TYPECLASS
from muddery.worlddata.data_sets import DATA_SETS
from muddery.utils.builder import build_object
from muddery.utils.loot_handler import LootHandler
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO
from muddery.utils.utils import search_obj_data_key
from muddery.utils.localized_strings_handler import _


@typeclass_mapping("BASE_CHARACTER")
class MudderyCharacter(TYPECLASS("BASE_OBJECT"), DefaultCharacter):
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
    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, DATA_SETS.character_loot_list.model)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()

        # set default values
        if not self.attributes.has("level"):
            self.db.level = 1
        if not self.attributes.has("exp"):
            self.db.exp = 0
        if not self.attributes.has("hp"):
            self.db.hp = 1
        if not self.attributes.has("team"):
            self.db.team = 0

        # init equipments
        if not self.attributes.has("equipments"):
            self.db.equipments = {}
        if not self.attributes.has("position_names"):
            self.db.position_names = {}
        self.reset_equip_positions()

        if not self.attributes.has("skills"):
            self.db.skills = {}

        # set quests
        if not self.attributes.has("completed_quests"):
            self.db.completed_quests = set()
        if not self.attributes.has("current_quests"):
            self.db.current_quests = {}
        
        # skill's gcd
        self.skill_gcd = GAME_SETTINGS.get("global_cd")
        self.auto_cast_skill_cd = GAME_SETTINGS.get("auto_cast_skill_cd")
        self.gcd_finish_time = 0
        
        # loop for auto cast skills
        self.auto_cast_loop = None
        
        self.target = None
        self.reborn_time = 0
        
        # A temporary character will be deleted after the combat finished.
        self.is_temp = False


    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.

        All skills, contents will be removed too.
        """
        result = super(MudderyCharacter, self).at_object_delete()
        if not result:
            return result
            
        # leave combat
        if self.ndb.combat_handler:
            self.ndb.combat_handler.remove_character(self)
        
        # stop auto casting
        self.stop_auto_combat_skill()
        
        # delete all skills
        for skill in self.db.skills.values():
            skill.delete()

        # delete all contents
        for content in self.contents:
            content.delete()
        
        return True
                            
    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyCharacter, self).after_data_loaded()
        
        # skill's ai
        ai_choose_skill_class = class_from_module(settings.AI_CHOOSE_SKILL)
        self.ai_choose_skill = ai_choose_skill_class()

        # skill's gcd
        self.skill_gcd = GAME_SETTINGS.get("global_cd")
        self.auto_cast_skill_cd = GAME_SETTINGS.get("auto_cast_skill_cd")
        self.gcd_finish_time = 0
        
        # loop for auto cast skills
        self.auto_cast_loop = None

        # clear target
        self.target = None

        # set reborn time
        self.reborn_time = getattr(self.dfield, "reborn_time", 0)

        # A temporary character will be deleted after the combat finished.
        self.is_temp = False

        # update equipment positions
        self.reset_equip_positions()

        # load default skills
        self.load_default_skills()

        # load default objects
        self.load_default_objects()

        # refresh data
        self.refresh_data()
        
    def after_data_key_changed(self):
        """
        Called at data_key changed.
        """
        super(MudderyCharacter, self).after_data_key_changed()

        # reset hp
        self.db.hp = self.max_hp

    def reset_equip_positions(self):
        """
        Reset equipment's position data.
        Returns:
            None
        """
        positions = []
        self.db.position_names = {}

        # reset equipment's position
        for record in DATA_SETS.equipment_positions.objects.all():
            positions.append(record.key)
            self.db.position_names[record.key] = record.name

        for position in self.db.equipments:
            if position not in positions:
                del self.db.equipments[position]

        for position in positions:
            if position not in self.db.equipments:
                self.db.equipments[position] = None

        # reset equipments status
        equipped = set()
        equipments = self.db.equipments
        for position in equipments:
            if equipments[position]:
                equipped.add(equipments[position])

        for content in self.contents:
            if content.dbref in equipped:
                content.equipped = True

    def set_level(self, level):
        """
        Set character's level.
        Args:
            level: character's new level

        Returns:
            None
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
        self.load_model_data()
        self.load_custom_attributes(CHARACTER_ATTRIBUTES_INFO)
        
        # load equips
        self.ues_equipments()

        # load passive skills
        self.cast_passive_skills()

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description and available commands.
        info = super(MudderyCharacter, self).get_appearance(caller)
        info["max_hp"] = self.max_hp
        info["hp"] = self.db.hp

        return info

    def change_status(self, increments):
        """
        Change the value of specified status.
        
        Args:
            increments: (dict) values to change.
            
        Return:
            (dict) values that actrually changed.
        """
        changes = {}
        for key in increments:
            changes[key] = 0

            if self.attributes.has(key):
                # try to add to self's db
                target = self.db
            elif hasattr(self, key):
                # try to add to self's attribute
                target = self
            elif self.custom_attributes_handler.has(key):
                # try to add to self's cattr
                target = self.cattr
            else:
                # no target
                continue

            origin_value = getattr(target, key)
            increment = increments[key]
            
            # check limits
            max_key = "max_" + key
            max_source = None
            if self.attributes.has(max_key):
                # try to add to self's db
                max_source = self.db
            elif hasattr(self, max_key):
                # try to add to self's attribute
                max_source = self
            elif self.custom_attributes_handler.has(max_key):
                # try to add to self's cattr
                max_source = self.cattr

            if max_source is not None:
                max_value = getattr(max_source, max_key)
                if origin_value + increment > max_value:
                    increment = max_value - origin_value
            
            min_value = 0
            min_key = "min_" + key
            min_source = None
            if self.attributes.has(min_key):
                # try to add to self's db
                min_source = self.db
            elif hasattr(self, min_key):
                # try to add to self's attribute
                min_source = self
            elif self.custom_attributes_handler.has(min_key):
                # try to add to self's cattr
                min_source = self.cattr

            if min_source is not None:
                min_value = getattr(min_source, min_key)

            if origin_value + increment < min_value:
                increment = min_value - origin_value

            # set value
            if increment != 0:
                setattr(target, key, origin_value + increment)
                changes[key] = increment
            
        return changes
        
    def get_combat_status(self):
        """
        Get character status used in combats.
        """
        return {"max_hp": self.max_hp,
                "hp": self.db.hp}

    def load_model_data(self):
        """
        Load character's level data.
        """
        model_name = getattr(self.dfield, "model", None)
        if not model_name:
            model_name = self.get_data_key()

        try:
            # get data from db
            model_data = DATA_SETS.character_models.objects.get(key=model_name, level=self.db.level)

            reserved_fields = {"id", "key", "name", "level"}
            for field in model_data._meta.fields:
                if field.name in reserved_fields:
                    continue
                setattr(self.dfield, field.name, model_data.serializable_value(field.name))
        except Exception, e:
            logger.log_errmsg("Can't load character %s's level info (%s, %s): %s" %
                              (self.get_data_key(), model_name, self.db.level, e))

        self.max_exp = getattr(self.dfield, "max_exp", 0)
        self.max_hp = getattr(self.dfield, "max_hp", 1)
        self.give_exp = getattr(self.dfield, "give_exp", 0)

    def search_inventory(self, obj_key):
        """
        Search specified object in the inventory.
        """
        result = [item for item in self.contents if item.get_data_key() == obj_key]
        return result

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

    def ues_equipments(self):
        """
        Add equipment's attributes to the character
        """
        # find equipments
        equipped = set([equip_id for equip_id in self.db.equipments.values() if equip_id])

        # add equipment's attributes
        for content in self.contents:
            if content.dbref in equipped:
                content.equip_to(self)

    def load_default_skills(self):
        """
        Load character's default skills.
        """
        # get character's model name
        model_name = getattr(self.dfield, "model", None)
        if not model_name:
            model_name = self.get_data_key()

        # default skills
        skill_records = DATA_SETS.default_skills.objects.filter(character=model_name)
        default_skill_ids = set([record.skill for record in skill_records])

        # remove old default skills
        for key, skill in self.db.skills.iteritems():
            if not skill:
                del self.db.skills[key]
            elif skill.is_default() and key not in default_skill_ids:
                # remove this skill
                skill.delete()
                del self.db.skills[key]

        # add new default skills
        for skill_record in skill_records:
            if skill_record.skill not in self.db.skills:
                self.learn_skill(skill_record.skill, True)

    def load_default_objects(self):
        """
        Load character's default objects.
        """
        pass

    def at_after_move(self, source_location, **kwargs):
        """
        Called after move has completed, regardless of quiet mode or
        not.  Allows changes to the object due to the location it is
        now in.

        Args:
            source_location : (Object) Where we came from. This may be `None`.

        """
        pass

    ########################################
    #
    # Skill methods.
    #
    ########################################
    
    def learn_skill(self, skill_key, is_default):
        """
        Learn a new skill.

        Args:
            skill_key: (string) skill's key
            is_default: (boolean) if it is a default skill

        Returns:
            (boolean) learned skill
        """
        if skill_key in self.db.skills:
            self.msg({"msg": _("You have already learned this skill.")})
            return False

        # Create skill object.
        skill_obj = build_object(skill_key)
        if not skill_obj:
            self.msg({"msg": _("Can not learn this skill.")})
            return False

        # set default
        if is_default:
            skill_obj.set_default(is_default)

        # Store new skill.
        skill_obj.set_owner(self)
        self.db.skills[skill_key] = skill_obj

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.refresh_data()

        # Notify the player
        if self.has_account:
            self.show_status()
            self.show_skills()
            self.msg({"msg": _("You learned skill {c%s{n.") % skill_obj.get_name()})

        return True

    def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.
        """
        time_now = time.time()
        if time_now < self.gcd_finish_time:
            # In GCD.
            self.msg({"skill_cast": {"cast": _("Global cooling down!")}})
            return

        if skill_key not in self.db.skills:
            self.msg({"skill_cast": {"cast": _("You do not have this skill.")}})
            return

        skill = self.db.skills[skill_key]
        if not skill.cast_skill(target, passive=False):
            return

        if self.skill_gcd > 0:
            # set GCD
            self.gcd_finish_time = time_now + self.skill_gcd

        # send CD to the player
        cd = {"skill": skill_key,               # skill's key
              "cd": skill.cd,                   # skill's cd
              "gcd": self.skill_gcd}

        self.msg({"skill_cd": cd})
        return

    def auto_cast_skill(self):
        """
        Cast a new skill automatically.
        """
        if not self.is_alive():
            return

        if not self.is_in_combat():
            # combat is finished, stop ticker
            self.stop_auto_combat_skill()
            return

        # Choose a skill and the skill's target.
        result = self.ai_choose_skill.choose(self)
        if result:
            skill, target = result
            self.ndb.combat_handler.prepare_skill(skill, self, target)
            
    def cast_passive_skills(self):
        """
        Cast all passive skills.
        """
        for skill in self.db.skills.values():
            if skill.passive:
                skill.cast_skill(self, passive=True)
                
    def start_auto_combat_skill(self):
        """
        Start auto cast skill.
        """
        if self.auto_cast_loop and self.auto_cast_loop.running:
            return

        # Cast a skill immediately
        # self.auto_cast_skill()

        # Set timer of auto cast.
        self.auto_cast_loop = task.LoopingCall(self.auto_cast_skill)
        self.auto_cast_loop.start(self.auto_cast_skill_cd)

    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        if self.auto_cast_loop and self.auto_cast_loop.running:
            self.auto_cast_loop.stop()


    ########################################
    #
    # Attack a target.
    #
    ########################################
    def set_target(self, target):
        """
        Set character's target.

        Args:
            target: (object) character's target

        Returns:
            None
        """
        self.target = target

    def clear_target(self):
        """
        Clear character's target.
        """
        self.target = None

    def attack_target(self, target, desc=""):
        """
        Attack a target.

        Args:
            target: (object) the target object.
            desc: (string) string to describe this attack

        Returns:
            (boolean) attack begins
        """
        if self.is_in_combat():
            # already in battle
            logger.log_errmsg("%s is already in battle." % self.dbref)
            return False

        # search target
        if not target:
            logger.log_errmsg("Can not find the target.")
            return False

        if not target.is_typeclass(settings.BASE_GENERAL_CHARACTER_TYPECLASS, exact=False):
            # Target is not a character.
            logger.log_errmsg("Can not attack the target %s." % target.dbref)
            return False

        if target.is_in_combat():
            # obj is already in battle
            logger.log_errmsg("%s is already in battle." % target.dbref)
            return False

        # create a new combat handler
        chandler = create_script(settings.NORMAL_COMBAT_HANDLER)
                        
        # set combat team and desc
        chandler.set_combat({1: [target], 2: [self]}, desc, 0)

        return True

    def attack_current_target(self, desc=""):
        """
        Attack current target.

        Args:
            desc: (string) string to describe this attack

        Returns:
            None
        """
        self.attack_target(self.target, desc)

    def attack_target_dbref(self, target_dbref, desc=""):
        """
        Attack a target by dbref.

        Args:
            target_dbref: (string) the dbref of the target.
            desc: (string) string to describe this attack

        Returns:
            None
        """
        target = self.search_dbref(target_dbref)
        self.attack_target(target, desc)

    def attack_temp_current_target(self, desc=""):
        """
        Attack current target's temporary clone object.

        Args:
            desc: (string) string to describe this attack

        Returns:
            None
        """
        self.attack_temp_target(self.target.get_data_key(), self.target.db.level, desc)

    def attack_temp_target(self, target_key, target_level=0, desc=""):
        """
        Attack a temporary clone of a target. This creates a new character object for attack.
        The origin target will not be affected.

        Args:
            target_key: (string) the info key of the target.
            target_level: (int) target's level
            desc: (string) string to describe this attack

        Returns:
            (boolean) fight begins
        """
        if target_level == 0:
            # Find the target and get its level.
            obj = search_obj_data_key(target_key)
            if not obj:
                logger.log_errmsg("Can not find the target %s." % target_key)
                return False
            obj = obj[0]
            target_level = obj.db.level

        # Create a target.
        target = build_object(target_key, set_location=False)
        if not target:
            logger.log_errmsg("Can not create the target %s." % target_key)
            return False

        target.set_level(target_level)
        target.is_temp = True
        return self.attack_target(target, desc)

    def is_in_combat(self):
        """
        Check if the character is in combat.

        Returns:
            (boolean) is in combat or not
        """
        return bool(self.ndb.combat_handler)

    def set_team(self, team_id):
        """
        Set character's team id in combat.

        Args:
            team_id: team's id

        Returns:
            None
        """
        self.db.team = team_id

    def get_team(self):
        """
        Get character's team id in combat.

        Returns:
            team id
        """
        return self.db.team

    def is_alive(self):
        """
        Check if the character is alive.

        Returns:
            (boolean) the character is alive or not
        """
        return round(self.db.hp) > 0

    def die(self, killers):
        """
        This character die.

        Args:
            killers: (list of objects) characters who kill this

        Returns:
            None
        """
        # trigger event
        self.event.at_character_die()
        self.event.at_character_kill(killers)

        if not self.is_temp and self.reborn_time > 0:
            # Set reborn timer.
            self.defer = deferLater(reactor, self.reborn_time, self.reborn)

    def reborn(self):
        """
        Reborn after being killed.
        """
        # Recover all hp.
        self.db.hp = self.max_hp

        # Reborn at its home.
        if self.home:
            self.move_to(self.home, quiet=True)
        
    def get_combat_commands(self):
        """
        This returns a list of combat commands.

        Returns:
            (list) available commands for combat
        """
        commands = []
        for key, skill in self.db.skills.iteritems():
            if skill.passive:
                # exclude passive skills
                continue

            command = {"name": skill.get_name(),
                       "key": key,
                       "icon": getattr(skill, "icon", None)}

            commands.append(command)

        return commands

    def provide_exp(self, killer):
        """
        Calculate the exp provide to the killer.
        Args:
            killer: (object) the character who kills it.

        Returns:
            (int) experience give to the killer
        """
        if killer:
            return self.give_exp

        return 0

    def add_exp(self, exp, combat=False):
        """
        Add character's exp.
        Args:
            exp: the exp value to add.

        Returns:
            None
        """
        self.db.exp += exp
        while self.db.exp >= self.max_exp:
            if self.max_exp > 0:
                # can upgrade
                self.db.exp -= self.max_exp
                self.level_up()
            else:
                # can not upgrade
                self.db.exp = 0
                break

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        self.set_level(self.db.level + 1)

        # recover hp
        self.db.hp = self.max_hp

    def show_status(self):
        """
        Show character's status.
        """
        pass

        
