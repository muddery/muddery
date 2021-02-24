"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import time, ast, traceback
from twisted.internet import reactor, task
from twisted.internet.task import deferLater
from django.conf import settings
from evennia.objects.objects import DefaultCharacter
from evennia import create_script
from evennia.utils import logger, search
from evennia.utils.utils import lazy_property, class_from_module
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.dao.equipment_positions import EquipmentPositions
from muddery.server.dao.loot_list import CharacterLootList
from muddery.server.dao.object_properties import ObjectProperties
from muddery.server.dao.default_skills import DefaultSkills
from muddery.server.utils.builder import build_object
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils import defines, utils
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.utils.utils import search_obj_data_key
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.builder import delete_object
from muddery.server.utils.defines import CombatType


class MudderyCharacter(ELEMENT("OBJECT"), DefaultCharacter):
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

    States:
        skills
        inventory
        level
        equipments
        closed_events
    """
    element_key = "CHARACTER"
    element_name = _("Character", "elements")
    model_name = "characters"

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, CharacterLootList.get(self.get_data_key()))

    @lazy_property
    def body_data_handler(self):
        return DataFieldHandler(self)

    # @property body stores character's body properties before using equipments and skills.
    def __body_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._body_holder
        except AttributeError:
            self._body_holder = ConstDataHolder(self, "body_properties", manager_name='body_data_handler')
            return self._body_holder

    # @body.setter
    def __body_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use self.body.name=value instead."
        raise Exception(string)

    # @body.deleter
    def __body_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the body object!")
    body = property(__body_get, __body_set, __body_del)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()

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
        # leave combat
        if self.ndb.combat_handler:
            self.ndb.combat_handler.leave_combat(self)
        
        # stop auto casting
        self.stop_auto_combat_skill()

        result = super(MudderyCharacter, self).at_object_delete()
        if not result:
            return result
        return True

    def after_creation(self):
        """
        Called once, after the object is created by Muddery.
        """
        # refresh the character's properties.
        self.refresh_properties(False)

    def load_custom_data(self, level):
        """
        Load body properties from db. Body properties do no include mutable properties.
        """
        # Get object level.
        if level is None:
            level = self.get_level()

        # Load values from db.
        data_key = self.const.clone if self.const.clone else self.get_data_key()

        values = {}
        for record in ObjectProperties.get_properties(data_key, level):
            key = record.property
            serializable_value = record.value
            if serializable_value == "":
                value = None
            else:
                try:
                    value = ast.literal_eval(serializable_value)
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = serializable_value
            values[key] = value

        # Set body values.
        for key, info in self.get_properties_info().items():
            if not info["mutable"]:
                self.const_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
                self.body_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
            else:
                # Set default mutable properties to prop.
                if not self.states.has(key):
                    self.states.save(key, self.get_custom_data_value(info["default"]))

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyCharacter, self).after_data_loaded()

        # get level
        level = self.states.load("level")
        if not level:
            self.states.save("level", 1)

        # friendly
        self.friendly = self.const.friendly if self.const.friendly else 0
        
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
        self.reborn_time = self.const.reborn_time if self.const.reborn_time else 0

        # A temporary character will be deleted after the combat finished.
        self.is_temp = False

        # update equipment positions
        self.reset_equip_positions()

        # load default skills
        self.load_default_skills()

        # load default objects
        self.load_default_objects()

        # refresh the character's properties.
        self.refresh_properties(True)

    def set_level(self, level):
        """
        Set object's level.
        Args:
            level: object's new level

        Returns:
            None
        """
        super(MudderyCharacter, self).set_level(level)
        self.refresh_properties(False)

    def reset_equip_positions(self):
        """
        Reset equipment's position data.
        Returns:
            None
        """
        # get equipment's position
        positions = set([r.key for r in EquipmentPositions.all()])

        inventory = self.states.load("inventory", [])
        equipments = self.states.load("equipments", {})

        changed = False
        for pos in list(equipments.keys()):
            if pos not in positions:
                inventory.append(equipments[pos])
                del equipments[pos]
                changed = True

        if changed:
            # Save changes.
            with self.states.atomic():
                self.states.save("equipments", equipments)
                self.states.save("inventory", inventory)

    def refresh_properties(self, keep_values):
        """
        Refresh character's final properties.

        Args:
            keep_values (boolean): mutable values keep last values.
        """
        if keep_values:
            last_properties = self.states.all()

        # Load body properties.
        for key, value in self.body_data_handler.all().items():
            self.const_data_handler.add(key, value)

        # load equips
        self.wear_equipments()

        # load passive skills
        self.cast_passive_skills()

        if keep_values:
            for key, info in self.get_properties_info().items():
                if info["mutable"]:
                    value = last_properties[key]

                    # check limits
                    max_key = "max_" + key
                    if self.const_data_handler.has(max_key):
                        max_value = self.const_data_handler.get(max_key)
                        if value > max_value:
                            value = max_value

                    min_key = "min_" + key
                    if self.const_data_handler.has(min_key):
                        min_value = self.const_data_handler.get(min_key)
                        if value < min_value:
                            value = min_value

                    # Set the value.
                    self.const_data_handler.add(key, value)

    @classmethod
    def get_event_trigger_types(cls):
        """
        Get an object's available event triggers.
        """
        return [defines.EVENT_TRIGGER_KILL,
                defines.EVENT_TRIGGER_DIE]

    def close_event(self, event_key):
        """
        If an event is closed, it will never be triggered.

        Args:
            event_key: (string) event's key
        """
        # set closed events
        closed_events = self.states.load("closed_events", set())
        closed_events.add(event_key)
        self.states.save("closed_events", closed_events)

    def is_event_closed(self, event_key):
        """
        Return True If this event is closed.

        Args:
            event_key: (string) event's key
        """
        closed_events = self.states.load("closed_events", set())
        return event_key in closed_events

    def get_combat_status(self):
        """
        Get character status used in combats.
        """
        return {}

    def total_object_number(self, obj_key):
        """
        Search specified object in the inventory.
        """
        inventory = self.states.load("inventory", [])
        equipments = self.states.load("equipments", {})

        objects = [item["number"] for item in inventory if item["key"] == obj_key]
        total = sum(objects)
        for item in equipments.values():
            if item["key"] == obj_key:
                total += 1

        return total

    def has_object(self, obj_key):
        """
        Check specified object in the inventory.
        """
        return self.total_object_number(obj_key) > 0

    def wear_equipments(self):
        """
        Add equipment's attributes to the character
        """
        # find equipments
        equipments = self.states.load("equipments", {})

        # add equipment's attributes
        for item in equipments.values():
            item["obj"].equip_to(self)

    def load_default_skills(self):
        """
        Load character's default skills.
        """
        # default skills
        skill_records = DefaultSkills.get(self.get_data_key())
        default_skill_ids = set([record.skill for record in skill_records])

        # remove old default skills
        skills = self.states.load("skills", {})
        changed = False
        for key in list(skills.keys()):
            skill = skills[key]
            if not skill:
                del skills[key]
                changed = True
            elif skill.is_default() and key not in default_skill_ids:
                # remove this skill
                skill.delete()
                del self.states.skills[key]
                changed = True

        if changed:
            self.states.save("skills", skills)

        # add new default skills
        for skill_record in skill_records:
            if skill_record.skill not in skills:
                self.learn_skill(skill_record.skill, True, True)

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

    def get_skills(self):
        """
        Get all skills.
        :return:
        """
        skills = self.states.load("skills", {})
        return skills

    def get_skill(self, key):
        """
        Get all skills.

        :arg
        key: (string) skill's key

        :return:
        skill object
        """
        skills = self.states.load("skills", {})
        return skills.get(key, None)

    def learn_skill(self, skill_key, is_default, silent):
        """
        Learn a new skill.

        Args:
            skill_key: (string) skill's key
            is_default: (boolean) if it is a default skill
            silent: (boolean) do not show messages to the player

        Returns:
            (boolean) learned skill
        """
        skills = self.states.load("skills", {})
        if skill_key in skills:
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
        skills[skill_key] = skill_obj
        self.states.save("skills", skills)

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.refresh_properties(True)

        # Notify the player
        if not silent and self.has_account:
            self.show_status()
            self.show_skills()
            self.msg({"msg": _("You learned skill {C%s{n.") % skill_obj.get_name()})

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

        skills = self.states.load("skills", {})
        if skill_key not in skills:
            self.msg({"skill_cast": {"cast": _("You do not have this skill.")}})
            return

        skill = skills[skill_key]
        cast_result = skill.cast(self, target)
        if not cast_result:
            return

        if self.skill_gcd > 0:
            # set GCD
            self.gcd_finish_time = time_now + self.skill_gcd

        skill_cd = {
            "skill_cd": {
                "skill": skill_key,  # skill's key
                "cd": skill.cd,  # skill's cd
                "gcd": self.skill_gcd
            }
        }

        skill_result = {
            "skill_cast": cast_result
        }

        self.msg(skill_cd)

        # send skill result to the player's location
        if self.is_in_combat():
            self.ndb.combat_handler.msg_all(skill_result)
        else:
            if self.location:
                # send skill result to its location
                self.location.msg_contents(skill_result)
            else:
                self.msg(skill_result)

        return

    def cast_combat_skill(self, skill_key, target):
        """
        Cast a skill in combat.
        """
        if self.is_in_combat():
            self.ndb.combat_handler.prepare_skill(skill_key, self, target)

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
            self.cast_combat_skill(skill, target)

    def is_auto_cast_skill(self):
        """
        If the character is casting skills automatically.
        """
        # auto cast skill
        return self.auto_cast_loop and self.auto_cast_loop.running

    def cast_passive_skills(self):
        """
        Cast all passive skills.
        """
        skills = self.states.load("skills", {})
        for skill in skills.values():
            if skill.passive:
                skill.cast(self, self)
                
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
        if hasattr(self, "auto_cast_loop") and self.auto_cast_loop and self.auto_cast_loop.running:
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

        if not target.is_typeclass(ELEMENT(settings.GENERAL_CHARACTER_ELEMENT_KEY), exact=False):
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
        chandler.set_combat(
            combat_type=CombatType.NORMAL,
            teams={1: [target], 2: [self]},
            desc=desc,
            timeout=0
        )

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
        self.attack_temp_target(self.target.get_data_key(), self.target.get_level(), desc)

    def attack_temp_target(self, target_key, target_level=0, desc=""):
        """
        Attack a temporary clone of a target. This creates a new character object for attack.
        The origin target will not be affected.

        Args:
            target_key: (string) the info key of the target object.
            target_level: (int) target object's level
            desc: (string) string to describe this attack

        Returns:
            (boolean) fight begins
        """
        if target_level == 0:
            # Find the target and get its level.
            obj = search_obj_data_key(target_key)
            if obj:
                obj = obj[0]
                target_level = obj.get_level()

        # Create a target.
        target = build_object(target_key, target_level, reset_location=False)
        if not target:
            logger.log_errmsg("Can not create the target %s." % target_key)
            return False

        target.is_temp = True
        return self.attack_target(target, desc)

    def is_in_combat(self):
        """
        Check if the character is in combat.

        Returns:
            (boolean) is in combat or not
        """
        return bool(self.ndb.combat_handler)

    def combat_result(self, combat_type, result, opponents=None, rewards=None):
        """
        Set the combat result.

        :param combat_type: combat's type
        :param result: defines.COMBAT_WIN, defines.COMBAT_LOSE, or defines.COMBAT_DRAW
        :param opponents: combat opponents
        :param rewards: combat rewards
        """
        pass

    def leave_combat(self):
        """
        Leave the current combat.
        """
        # remove combat commands
        self.cmdset.delete(settings.CMDSET_COMBAT)

        if self.ndb.combat_handler:
            self.ndb.combat_handler.leave_combat(self)
            del self.ndb.combat_handler

        if self.is_temp:
            # delete template character and notify its location
            location = self.location

            delete_object(self.dbref)
            if location:
                for content in location.contents:
                    if content.has_account:
                        content.show_location()

    def set_team(self, team_id):
        """
        Set character's team id in combat.

        Args:
            team_id: team's id

        Returns:
            None
        """
        self.states.save("team", team_id)

    def get_team(self):
        """
        Get character's team id in combat.

        Returns:
            team id
        """
        return self.states.load("team", 0)

    def is_alive(self):
        """
        Check if the character is alive.

        Returns:
            (boolean) the character is alive or not
        """
        return True

    def die(self, killers):
        """
        This character die.

        Args:
            killers: (list of objects) characters who kill this

        Returns:
            None
        """
        if not self.is_temp and self.reborn_time > 0:
            # Set reborn timer.
            self.defer = deferLater(reactor, self.reborn_time, self.reborn)

    def reborn(self):
        """
        Reborn after being killed.
        """
        # Reborn at its home.
        home = None
        if not home:
            home_key = self.const.location
            if home_key:
                rooms = utils.search_obj_data_key(home_key)
                if rooms:
                    home = rooms[0]

        if not home:
            rooms = search.search_object(settings.DEFAULT_HOME)
            if rooms:
                home = rooms[0]

        if home:
            self.move_to(home, quiet=True)

        # Recover properties.
        self.recover()

    def recover(self):
        """
        Recover properties.
        """
        pass
        
    def get_combat_commands(self):
        """
        This returns a list of combat commands.

        Returns:
            (list) available commands for combat
        """
        commands = []
        skills = self.states.load("skills", {})
        for key, skill in skills.items():
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
        return 0

    def add_exp(self, exp):
        """
        Add character's exp.
        Args:
            exp: the exp value to add.

        Returns:
            None
        """
        pass

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        level = self.get_level()
        self.set_level(level + 1)

    def show_status(self):
        """
        Show character's status.
        """
        pass

    def get_name(self):
        name = super(MudderyCharacter, self).get_name()

        if not self.is_alive():
            name += _(" [DEAD]")

        return name
