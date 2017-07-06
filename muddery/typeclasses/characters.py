"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

import ast
from twisted.internet import reactor
from twisted.internet.task import deferLater
from django.conf import settings
from evennia.objects.objects import DefaultCharacter
from evennia import create_script
from evennia.typeclasses.models import DbHolder
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.typeclasses.objects import MudderyObject
from muddery.utils import utils
from muddery.utils.builder import build_object
from muddery.utils.skill_handler import SkillHandler
from muddery.utils.loot_handler import LootHandler
from muddery.worlddata.data_sets import DATA_SETS
from muddery.utils.builder import delete_object
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO
from muddery.utils.localized_strings_handler import _


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
        if not self.attributes.has("mp"):
            self.db.mp = 1
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
        
        self.target = None
        self.reborn_time = 0
        
        # A temporary character will be deleted after the combat finished.
        self.is_temp = False

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyCharacter, self).after_data_loaded()

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
        for skill in self.db.skills:
            skill_obj = self.db.skills[skill]
            if skill_obj.is_default() and skill not in default_skill_ids:
                # remove this skill
                skill_obj.delete()
                del self.db.skills[skill]

        # add new default skills
        for skill_record in skill_records:
            if not self.skill_handler.has_skill(skill_record.skill):
                self.skill_handler.learn_skill(skill_record.skill, True)
                
    def cast_passive_skills(self):
        """
        Add passive skills' effects to the character
        """
        # cast passive skills
        self.skill_handler.cast_passive_skills()

    def load_default_objects(self):
        """
        Load character's default objects.
        """
        pass

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
    
    def learn_skill(self, skill_key):
        """
        Check if the character has this skill.

        Args:
            skill_key: (string) skill's key

        Returns:
            (boolean) If the character learned this skill.
        """
        return self.skill_handler.learn_skill(skill_key)
        

    def has_skill(self, skill_key):
        """
        Check if the character has this skill.

        Args:
            skill_key: (string) skill's key

        Returns:
            (boolean) if the character has this skill or not
        """
        self.skill_handler.has_skill(skill_key)
        
    def prepare_skill(self, skill_key, target):
        """
        Prepare to cast a skill.
        """
        if self.is_in_combat():
            self.ndb.combat_handler.prepare_skill(skill_key, self, target)
        else:
            self.cast_skill(skill_key, target)

    def cast_skill(self, skill_key, target):
        """
        Cast a skill.
        """
        self.skill_handler.cast_skill(skill_key, target)

    def auto_cast_skill(self):
        """
        Auto cast an available skill.
        Put this method on the character because TICKER_HANDLER needs a typeclass.

        Returns:
            None
        """
        self.skill_handler.auto_cast_skill()

    def send_skill_result(self, result):
        """
        Set the result of the skill. The character can send these messages to its surroundings.

        Args:
            result: (dict)the result of the skill

        Returns:
            None
        """
        if result:
            if self.ndb.combat_handler:
                # send skill's result to the combat handler
                self.ndb.combat_handler.send_skill_result(result)
            elif self.location:
                # send skill's result to caller's location
                self.location.msg_contents({"skill_result": result})

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
        chandler = create_script(settings.COMBAT_HANDLER)
                        
        # set combat team and desc
        chandler.set_combat({1: [target], 2: [self]}, desc)

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
            obj = utils.search_obj_data_key(target_key)
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

    ########################################
    #
    # Combat methods.
    #
    ########################################
    def at_enter_combat_mode(self, combat_handler):
        """
        Called when the character enters a combat.

        Returns:
            None
        """
        if not combat_handler:
            return

        # add the combat handler
        self.ndb.combat_handler = combat_handler

        # Change the command set.
        self.cmdset.add(settings.CMDSET_COMBAT)

    def at_combat_start(self):
        """
        Called when the combat begins.

        Returns:
            None
        """
        pass

    def at_combat_win(self, winners, losers):
        """
        Called when the character wins the combat.
        
        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        # add exp
        # get total exp
        exp = 0
        for loser in losers:
            exp += loser.provide_exp(self)

        if exp:
            # give experience to the winner
            self.add_exp(exp, combat=True)

    def at_combat_lose(self, winners, losers):
        """
        Called when the character loses the combat.
        
        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        # The character is killed.
        self.die(winners)

    def at_combat_escape(self):
        """
        Called when the character escaped from the combat.

        Returns:
            None
        """
        pass

    def at_leave_combat_mode(self):
        """
        Called when the character leaves a combat.

        Returns:
            None
        """
        # remove the combat handler
        del self.ndb.combat_handler

        # remove combat commands
        self.cmdset.delete(settings.CMDSET_COMBAT)
        
        if self.is_temp:
            # notify its location
            location = self.location
            delete_object(self.dbref)
            if location:
                for content in location.contents:
                    if content.has_player:
                        content.show_location()

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

        if self.reborn_time > 0:
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
        for key in self.db.skills:
            skill = self.db.skills[key]
            if skill.passive:
                # exclude passive skills
                continue

            command = {"name": skill.name,
                       "key": skill.get_data_key(),
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
