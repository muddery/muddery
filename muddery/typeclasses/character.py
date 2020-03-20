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
from evennia.typeclasses.models import DbHolder
from evennia.utils import logger, search
from evennia.utils.utils import lazy_property, class_from_module
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.worlddata.dao import common_mappers as CM
from muddery.worlddata.dao.loot_list_mapper import CHARACTER_LOOT_LIST
from muddery.worlddata.dao.object_properties_mapper import OBJECT_PROPERTIES
from muddery.worlddata.dao.default_skills_mapper import DEFAULT_SKILLS
from muddery.utils.builder import build_object
from muddery.utils.loot_handler import LootHandler
from muddery.utils import defines, utils
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.utils import search_obj_data_key
from muddery.utils.data_field_handler import DataFieldHandler
from muddery.utils.localized_strings_handler import _
from muddery.utils.builder import delete_object


class MudderyCharacter(TYPECLASS("OBJECT"), DefaultCharacter):
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
    typeclass_key = "CHARACTER"
    typeclass_name = _("Character", "typeclasses")
    model_name = "characters"

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, CHARACTER_LOOT_LIST.filter(self.get_data_key()))

    @lazy_property
    def body_properties_handler(self):
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
            self._body_holder = DbHolder(self, "body_properties", manager_name='body_properties_handler')
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

        # set default values
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
        if not self.attributes.has("finished_quests"):
            self.db.finished_quests = set()
        if not self.attributes.has("current_quests"):
            self.db.current_quests = {}

        # set closed events
        if not self.attributes.has("closed_events"):
            self.db.closed_events = set()
        
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
            self.ndb.combat_handler.leave_combat(self)
        
        # stop auto casting
        self.stop_auto_combat_skill()
        
        # delete all skills
        for skill in self.db.skills.values():
            skill.delete()

        # delete all contents
        for content in self.contents:
            content.delete()
        
        return True

    def load_custom_properties(self, level):
        """
        Load body properties from db. Body properties do no include mutable properties.
        """
        # Get object level.
        if level is None:
            level = self.db.level

        # Load values from db.
        data_key = self.get_data_key()
        clone = getattr(self.system, "clone", None)
        if clone:
            data_key = self.system.clone

        values = {}
        for record in OBJECT_PROPERTIES.get_properties(data_key, level):
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
                self.custom_properties_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
                self.body_properties_handler.add(key, values.get(key, ast.literal_eval(info["default"])))

        # Set default mutable custom properties.
        self.set_mutable_custom_properties()

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyCharacter, self).after_data_loaded()

        # get level
        if not self.db.level:
            self.db.level = getattr(self.system, "level", 1)

        # friendly
        self.friendly = getattr(self.system, "friendly", 0)
        
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
        self.reborn_time = getattr(self.system, "reborn_time", 0)

        # A temporary character will be deleted after the combat finished.
        self.is_temp = False

        # update equipment positions
        self.reset_equip_positions()

        # load default skills
        self.load_default_skills()

        # load default objects
        self.load_default_objects()

        # refresh the character's properties.
        self.refresh_properties()

    def set_level(self, level):
        """
        Set object's level.
        Args:
            level: object's new level

        Returns:
            None
        """
        super(MudderyCharacter, self).set_level(level)
        self.refresh_properties()

    def reset_equip_positions(self):
        """
        Reset equipment's position data.
        Returns:
            None
        """
        positions = []
        self.db.position_names = {}

        # reset equipment's position
        for record in CM.EQUIPMENT_POSITIONS.all():
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

    def refresh_properties(self):
        """
        Refresh character's final properties.
        """
        # Load body properties.
        for key, value in self.body_properties_handler.all(True):
            self.custom_properties_handler.add(key, value)

        # load equips
        self.wear_equipments()

        # load passive skills
        self.cast_passive_skills()

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
        self.db.closed_events.add(event_key)

    def is_event_closed(self, event_key):
        """
        Return True If this event is closed.

        Args:
            event_key: (string) event's key
        """
        return event_key in self.db.closed_events

    def change_properties(self, increments):
        """
        Change values of specified properties.
        
        Args:
            increments: (dict) values to change.
            
        Return:
            (dict) values that actually changed.
        """
        changes = {}
        properties_info = self.get_properties_info()

        for key, increment in increments.items():
            changes[key] = 0

            if not self.custom_properties_handler.has(key):
                continue

            origin_value = getattr(self.prop, key)
            
            # check limits
            max_key = "max_" + key
            if self.custom_properties_handler.has(max_key):
                max_value = getattr(self.prop, max_key)
                if origin_value + increment > max_value:
                    increment = max_value - origin_value

            # Default minimum value is 0.
            min_value = 0
            min_key = "min_" + key
            if self.custom_properties_handler.has(min_key):
                min_value = getattr(self.prop, min_key)

            if origin_value + increment < min_value:
                increment = min_value - origin_value

            # Set the value.
            if increment != 0:
                value = origin_value + increment
                self.custom_properties_handler.add(key, value)
                changes[key] = increment

        return changes

    def set_properties(self, values):
        """
        Set values of specified properties.

        Args:
            values: (dict) values to set.

        Return:
            (dict) values that actually set.
        """
        actual = {}
        properties_info = self.get_properties_info()

        for key, value in values.items():
            actual[key] = 0

            if not self.custom_properties_handler.has(key):
                continue

            # check limits
            max_key = "max_" + key
            if self.custom_properties_handler.has(max_key):
                max_value = getattr(self.prop, max_key)
                if value > max_value:
                    value = max_value

            # Default minimum value is 0.
            min_key = "min_" + key
            if self.custom_properties_handler.has(min_key):
                min_value = getattr(self.prop, min_key)
                if value < min_value:
                    value = min_value

            # Set the value.
            setattr(self.prop, key, value)
            actual[key] = value

        return actual

    def get_combat_status(self):
        """
        Get character status used in combats.
        """
        return {}

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
        self.refresh_properties()

    def wear_equipments(self):
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
        # default skills
        skill_records = DEFAULT_SKILLS.filter(self.get_data_key())
        default_skill_ids = set([record.skill for record in skill_records])

        # remove old default skills
        for key, skill in self.db.skills.items():
            if not skill:
                del self.db.skills[key]
            elif skill.is_default() and key not in default_skill_ids:
                # remove this skill
                skill.delete()
                del self.db.skills[key]

        # add new default skills
        for skill_record in skill_records:
            if skill_record.skill not in self.db.skills:
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
            self.refresh_properties()

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

        if skill_key not in self.db.skills:
            self.msg({"skill_cast": {"cast": _("You do not have this skill.")}})
            return

        skill = self.db.skills[skill_key]
        cast_result = skill.cast_skill(target)
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
                skill.cast_skill(self)
                
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

        if not target.is_typeclass(TYPECLASS(settings.GENERAL_CHARACTER_TYPECLASS_KEY), exact=False):
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
                target_level = obj.db.level

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

    def combat_result(self, result, opponents=None):
        """
        Set the combat result.

        :param result: defines.COMBAT_WIN, defines.COMBAT_LOSE, or defines.COMBAT_DRAW
        :param opponents: combat opponents
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
            home_key = self.system.location
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
        for key, skill in self.db.skills.items():
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
        self.set_level(self.db.level + 1)

    def show_status(self):
        """
        Show character's status.
        """
        pass
