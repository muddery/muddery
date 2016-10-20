"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

import random
from django.conf import settings
from django.apps import apps
from evennia.objects.objects import DefaultCharacter
from evennia import create_script
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.localized_strings_handler import LS
from muddery.utils import utils
from muddery.utils.builder import build_object
from muddery.utils.skill_handler import SkillHandler
from muddery.utils.loot_handler import LootHandler


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

    # initialize skill handler in a lazy fashion
    @lazy_property
    def skill_handler(self):
        return SkillHandler(self)

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, settings.CHARACTER_LOOT_LIST)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()

        # set default values
        self.db.level = 1
        self.db.exp = 0
        self.db.hp = 1
        self.db.mp = 1
        self.db.team = 0

        # init equipments
        self.db.equipments = {}
        self.db.position_names = {}
        self.reset_equip_positions()
        
        self.db.skills = {}

        # set quests
        self.db.completed_quests = set()
        self.db.current_quests = {}

        # set attributes
        self.db.attributes = {}

    def at_init(self):
        """
        Init the character.
        """
        super(MudderyCharacter, self).at_init()

        # update equipment positions
        self.reset_equip_positions()

        # clear target
        self.target = None

    def reset_equip_positions(self):
        """
        Reset equipment's position data.
        Returns:
            None
        """
        positions = []
        self.db.position_names = {}

        model_position = apps.get_model(settings.WORLD_DATA_APP, settings.EQUIPMENT_POSITIONS)
        if model_position:
            for record in model_position.objects.all():
                positions.append(record.key)
                self.db.position_names[record.key] = record.name

        for position in self.db.equipments:
            if position not in positions:
                del self.db.equipments[position]

        for position in positions:
            if position not in self.db.equipments:
                self.db.equipments[position] = None

    def load_data(self):
        """
        Set data_info to the object.
        """
        super(MudderyCharacter, self).load_data()

        # default skills
        skill_records = []
        default_skills = apps.get_model(settings.WORLD_DATA_APP, settings.DEFAULT_SKILLS)
        if default_skills:
            # Get records.
            model_name = getattr(self.dfield, "model", None)
            if not model_name:
                model_name = self.get_data_key()

            skill_records = default_skills.objects.filter(character=model_name)

        default_skill_ids = set([record.skill for record in skill_records])

        # remove old default skills
        for skill in self.db.skills:
            if self.db.skills[skill].is_default() and skill not in default_skill_ids:
                # remove this skill
                del self.db.skills[skill]

        # add new default skills
        for skill_record in skill_records:
            if not self.skill_handler.has_skill(skill_record.skill):
                self.skill_handler.learn_skill(skill_record.skill, True)

        # refresh data
        self.refresh_data()

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
        
        # load equips data
        self.load_equip_data()

        # load passive skill
        self.load_passive_skill_data()

    def load_model_data(self):
        """
        Load character's level data.
        """
        model_name = getattr(self.dfield, "model", None)
        if not model_name:
            model_name = self.get_data_key()

        try:
            # get data from db
            model_obj = apps.get_model(settings.WORLD_DATA_APP, settings.CHARACTER_MODELS)
            model_data = model_obj.objects.get(key=model_name, level=self.db.level)

            reserved_fields = {"id", "key", "level"}
            for field in model_data._meta.fields:
                if field.name in reserved_fields:
                    continue
                setattr(self.dfield, field.name, model_data.serializable_value(field.name))
        except Exception, e:
            logger.log_errmsg("Can't load character %s's level info (%s, %s): %s" %
                              (self.get_data_key(), model_name, self.db.level, e))

        self.max_exp = getattr(self.dfield, "max_exp", 0)
        self.max_hp = getattr(self.dfield, "max_hp", 1)
        self.max_mp = getattr(self.dfield, "max_mp", 1)
        self.attack = getattr(self.dfield, "attack", 0)
        self.defence = getattr(self.dfield, "defence", 0)
        self.give_exp = getattr(self.dfield, "give_exp", 0)

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
        Add equipment's attributes to the character
        """
        # find equipments
        equipped = set([equip_id for equip_id in self.db.equipments.values() if equip_id])

        # add equipment's attributes
        for content in self.contents:
            if content.dbref in equipped:
                for effect in settings.EQUIP_EFFECTS:
                    value = getattr(self, effect, 0)
                    value += getattr(content.dfield, effect, 0)
                    setattr(self, effect, value)

    def load_passive_skill_data(self):
        """
        Add passive skills' effects to the character
        """
        # cast passive skills
        self.skill_handler.cast_passive_skills()

    def set_initial_data(self):
        """
        Initialize this object after data loaded.
        """
        super(MudderyCharacter, self).set_initial_data()

        # set initial data
        self.db.hp = self.max_hp


    def use_object(self, obj, number=1):
        """
        Use an object.

        Args:
            obj: (object) object to use
            number: (int) number to use

        Returns:
            result: (string) the description of the result
        """
        if not obj:
            return LS("Can not find this object.")

        if obj.db.number < number:
            return LS("Not enough number.")

        # take effect
        try:
            result, used = obj.take_effect(self, number)
            if used > 0:
                # remove used object
                obj_list = [{"object": obj.get_data_key(),
                             "number": used}]
                self.remove_objects(obj_list)
            return result
        except Exception, e:
            ostring = "Can not use %s: %s" % (obj.get_data_key(), e)
            logger.log_tracemsg(ostring)

        return LS("No effect.")

    def at_after_move(self, source_location):
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

    def has_skill(self, skill):
        """
        Check if the character has this skill.

        Args:
            skill: (string) skill's key

        Returns:
            (boolean) if the character has this skill or not
        """
        self.skill_handler.has_skill(skill)

    def auto_cast_skill(self):
        """
        Auto cast an available skill.

        Returns:
            None
        """
        self.skill_handler.auto_cast_skill()

    def cast_skill_manually(self, skill, target):
        """
        Cast a skill.

        Args:
            skill: (string) skill's key
            target: (object) skill's target

        Returns:
            None
        """
        self.target = target
        self.skill_handler.cast_skill_manually(skill, target)

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
            None
        """
        if self.is_in_combat():
            # already in battle
            logger.log_errmsg("%s is already in battle." % self.dbref)
            return

        # search target
        if not target:
            logger.log_errmsg("Can not find the target.")
            return

        if not target.is_typeclass(settings.BASE_GENERAL_CHARACTER_TYPECLASS, exact=False):
            # Target is not a character.
            logger.log_errmsg("Can not attack the target %s." % target.dbref)
            return

        if target.is_in_combat():
            # obj is already in battle
            logger.log_errmsg("%s is already in battle." % target.dbref)
            return

        # create a new combat handler
        chandler = create_script(settings.COMBAT_HANDLER)
                        
        # set combat team and desc
        chandler.set_combat({1: [target], 2: [self]}, desc)

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
        target = self.search(target_dbref)
        self.attack_target(target, desc)

    def attack_target_key(self, target_key, desc=""):
        """
        Attack a target.

        Args:
            target_key: (string) the info key of the target.
            desc: (string) string to describe this attack

        Returns:
            None
        """
        target = self.search(target_key)
        self.attack_target(target, desc)

    def attack_clone_current_target(self, desc=""):
        """
        Attack current target.

        Args:
            desc: (string) string to describe this attack

        Returns:
            None
        """
        self.attack_clone_target(self.target.get_data_key(), self.target.db.level, desc)

    def attack_clone_target(self, target_key, target_level=0, desc=""):
        """
        Attack the image of a target. This creates a new character object for attack.
        The origin target will not be affected.

        Args:
            target_key: (string) the info key of the target.
            target_level: (int) target's level
            desc: (string) string to describe this attack

        Returns:
            None
        """
        if target_level == 0:
            # Find the target and get its level.
            obj = utils.search_obj_data_key(target_key)
            if not obj:
                logger.log_errmsg("Can not find the target %s." % target_key)
                return
            obj = obj[0]
            target_level = obj.db.level

        # Create a target.
        target = build_object(target_key)
        if not target:
            logger.log_errmsg("Can not create the target %s." % target_key)
            return

        target.set_level(target_level)
        self.attack_target(target, desc)

    ########################################
    #
    # Combat methods.
    #
    ########################################
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

    def hurt(self, damage):
        """
        Be hurted.

        Args:
            damage: (number) the damage value

        Returns:
            None
        """
        self.db.hp -= damage
        if self.db.hp < 0:
            self.db.hp = 0

    def is_alive(self):
        """
        Check if the character is alive.

        Returns:
            (boolean) the character is alive or not
        """
        return self.db.hp > 0

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

    def get_combat_commands(self):
        """
        This returns a list of combat commands.

        Returns:
            (list) available commands for combat
        """
        commands = []
        for key in self.db.skills:
            skill = self.db.skills[key]
            if skill.passive:
                # exclude passive skills
                continue

            command = {"name": skill.name,
                       "key": skill.get_data_key()}
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

    def add_exp(self, exp):
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

        self.msg({"get_exp": exp})

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        self.set_level(self.db.level + 1)

        # recover hp
        self.db.hp = self.max_hp

        if self.has_player:
            # notify the player
            self.msg({"msg": LS("{c%s upgraded to level %s.{n") % (self.get_name(), self.db.level)})
