"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import time, traceback, ast
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.loot_list import CharacterLootList
from muddery.server.database.worlddata.default_skills import DefaultSkills
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.character_states_dict import CharacterStatesDict
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils.game_settings import GameSettings
from muddery.server.utils.localized_strings_handler import _
from muddery.common.utils.defines import CombatType, EventType
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.common.utils.utils import class_from_path
from muddery.server.database.gamedata.object_storage import MemoryObjectStorage
from muddery.server.server import Server
from muddery.common.utils.utils import async_gather


CHARACTER_LAST_ID = 0


class MudderyCharacter(ELEMENT("MATTER")):
    """
    Characters can move in rooms.
    """
    element_type = "CHARACTER"
    element_name = "Character"
    model_name = "characters"

    last_id = 0

    skill_scheduler_id = "skill"
    reborn_scheduler_id = "reborn"

    @staticmethod
    def generate_id():
        """
        Generate an id.
        :return:
        """
        global CHARACTER_LAST_ID
        CHARACTER_LAST_ID += 1
        return CHARACTER_LAST_ID

    def __init__(self):
        """
        Initial the object.
        """
        super(MudderyCharacter, self).__init__()

        self.set_id(self.generate_id())
        self.states = None

        self.loot_handler = None
        self.location = None
        self.scheduler = None

        self.is_alive = True
        self.default_relationship = 0

        # character's skills
        # self.skills = {
        #    skill's key: {
        #       "obj": skill's object,
        #       "cd_finish": skill's cd time,
        #    }
        # }
        self.skills = {}

    def __del__(self):
        """
        Called when this object is deleted from the memory.
        :return:
        """
        # stop auto casting
        self.stop_auto_combat_skill()

    def create_status_handler(self):
        """
        Characters use memory to store status by default.
        :return:
        """
        return ObjectStatesHandler(self.get_id(), MemoryObjectStorage)

    def set_id(self, char_id):
        """
        Set the character's id.
        """
        self.id = char_id

    def get_id(self):
        """
        Get the character's id.
        :return:
        """
        return self.id

    def get_scheduler(self):
        # get the apscheduler
        if not self.scheduler:
            self.scheduler = AsyncIOScheduler(timezone=pytz.utc)
            self.scheduler.start()
        return self.scheduler

    async def at_element_setup(self, first_time):
        """
        Called when the object is loaded and initialized.

        """
        await super(MudderyCharacter, self).at_element_setup(first_time)

        self.set_name(self.const.name)
        self.set_desc(self.const.desc)
        self.set_icon(self.const.icon)

        self.states = self.create_status_handler()

        # default_relationship
        self.default_relationship = self.const.relationship if self.const.relationship else 0

        # skill's ai
        ai_choose_skill_class = class_from_path(SETTINGS.AI_CHOOSE_SKILL)
        self.ai_choose_skill = ai_choose_skill_class()

        # skill's gcd
        self.skill_gcd = GameSettings.inst().get("global_cd")
        self.auto_cast_skill_cd = GameSettings.inst().get("auto_cast_skill_cd")

        time_now = time.time()
        self.gcd_finish_time = time_now + self.skill_gcd

        # clear target
        self.target = None

        # set reborn time
        self.reborn_time = self.const.reborn_time if self.const.reborn_time else 0

        self.combat_id = None

        # load default skills
        await self.load_skills()

        # initialize loot handler
        self.loot_handler = LootHandler(CharacterLootList.get(self.get_element_key()))

    async def after_element_setup(self, first_time):
        """
        Called after the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        await super(MudderyCharacter, self).after_element_setup(first_time)

        await self.refresh_states(not first_time)

    async def refresh_states(self, keep_states):
        """
        Refresh character's states.

        Args:
            keep_states (boolean): states values keep last values.
        """
        # set states
        to_save = {}
        records = CharacterStatesDict.all()

        if keep_states and records:
            has_status = await async_gather([self.states.has(record.key) for record in records])
        else:
            has_status = []

        for index, record in enumerate(records):
            if keep_states and has_status[index]:
                # Do not change existent states.
                continue

            # set new states
            if self.const_data_handler.has(record.default):
                # the value of another const
                value = self.const_data_handler.get(record.default)
            else:
                try:
                    value = ast.literal_eval(record.default)
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = record.default

            # set the value.
            to_save[record.key] = value

        if to_save:
            await self.states.saves(to_save)

    async def load_custom_level_data(self, element_type, element_key, level):
        """
        Load custom's level data.

        :param level:
        :return:
        """
        # Get object level.
        if level is None:
            level = await self.get_level()

        # Clone another element's values.
        element_key = self.const.clone if self.const.clone else element_key
        await super(MudderyCharacter, self).load_custom_level_data(self.element_type, element_key, level)

    async def set_level(self, level):
        """
        Set element's level.
        :param level:
        :return:
        """
        self.level = level
        await self.load_custom_level_data(self.element_type, self.get_element_key(), level)

        await self.refresh_states(True)

    def get_name(self):
        """
        Get player character's name.
        """
        name = self.name
        if not self.is_alive:
            name += _(" [DEAD]")

        return name

    def get_appearance(self):
        """
        The common appearance for all players.
        """
        info = super(MudderyCharacter, self).get_appearance()
        info["id"] = self.get_id()

        return info

    @classmethod
    def get_event_trigger_types(cls):
        """
        Get an object's available event triggers.
        """
        return [
            EventType.EVENT_TRIGGER_KILL,
            EventType.EVENT_TRIGGER_DIE
        ]

    async def get_combat_status(self):
        """
        Get character status used in combats.
        """
        return {
            "id": self.get_id()
        }

    async def load_skills(self):
        """
        Load character's skills.
        """
        self.skills = {}

        # default skills
        default_skills = DefaultSkills.get(self.get_element_key())
        for index, item in enumerate(default_skills):
            # Store new skill.
            self.skills[item.skill] = {
                "level": item.level,
                "cd_finish": 0,
            }

        if self.skills:
            skills = await async_gather([self.create_skill(key, item["level"]) for key, item in self.skills.items()])
            for index, item in enumerate(self.skills.values()):
                item["obj"] = skills[index]

    async def create_skill(self, skill_key, level):
        """
        Create a skill object.
        """
        try:
            # Create skill object.
            skill_obj = ELEMENT("SKILL")()
            await skill_obj.setup_element(skill_key, level)
        except Exception as e:
            logger.log_err("Can not load skill %s: (%s) %s" % (skill_key, type(e).__name__, e))
            return

        return skill_obj

    def set_location(self, location):
        """
        Set the character's location (room) directly.
        :param location: a room
        :return:
        """
        self.location = location

    async def move_to(self, location):
        """
        The character moves from a room to another.
        :param location: a room
        :return:
        """
        if self.location:
            await self.location.at_character_leave(self)

        self.set_location(location)

        if self.location:
            self.location.at_character_arrive(self)

    def get_location(self):
        """
        Get the character's location room.
        :return:
        """
        return self.location

    async def msg(self, content):
        """
        Send a message to the character's player if it has.
        :param content:
        :return:
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
        return self.skills

    async def get_available_skills(self):
        """
        Get current available skills of a character.
        :param caller:
        :return: skills
        """
        time_now = time.time()
        if time_now < self.gcd_finish_time:
            return

        skills = []
        if self.skills:
            available = await async_gather([s["obj"].is_available(self, passive=False) for s in self.skills.values()])
            skills = [s["obj"] for i, s in enumerate(self.skills.values()) if time_now >= s["cd_finish"] and available[i]]

        return skills

    def get_skill(self, key):
        """
        Get all skills.

        :arg
        key: (string) skill's key

        :return:
        skill object
        """
        return self.skills.get(key, None)

    async def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.
        """
        skill_info = self.skills[skill_key]
        skill_obj = skill_info["obj"]

        if not await skill_obj.is_available(self, False):
            return

        time_now = time.time()
        if time_now < self.gcd_finish_time and time_now < skill_info["cd_finish"]:
            # In cd.
            return

        cast_result = await skill_obj.cast(self, target)

        if self.skill_gcd > 0:
            # set GCD
            self.gcd_finish_time = time_now + self.skill_gcd

        # save cd finish time
        self.skills[skill_key]["cd_finish"] = time_now + skill_obj.get_cd()

        skill_cd = {
            "skill_cd": {
                "skill": skill_key,  # skill's key
                "cd": skill_obj.get_cd(),  # skill's cd
                "gcd": self.skill_gcd
            }
        }

        skill_result = {
            "skill_cast": cast_result
        }

        await self.msg(skill_cd)

        # send skill result to the player's location
        combat = await self.get_combat()
        if combat:
            await combat.msg_all(skill_result)
        else:
            if self.location:
                # send skill result to its location
                await self.location.msg_characters(skill_result)
            else:
                await self.msg(skill_result)

        return

    async def cast_combat_skill(self, skill_key, target_id):
        """
        Cast a skill in combat.
        """
        combat = await self.get_combat()
        if combat:
            await combat.prepare_skill(skill_key, self, target_id)
        else:
            logger.log_err("Character %s is not in combat." % self.id)

    async def auto_cast_skill(self):
        """
        Cast a new skill automatically.
        """
        if not self.is_alive:
            return

        if not self.is_in_combat():
            # combat is finished, stop ticker
            self.stop_auto_combat_skill()
            return

        # Choose a skill and the skill's target.
        result = await self.ai_choose_skill.choose(self)
        if result:
            skill, target = result
            await self.cast_combat_skill(skill, target)

    def is_auto_cast_skill(self):
        """
        If the character is casting skills automatically.
        """
        scheduler = self.get_scheduler()
        return scheduler.get_job(self.skill_scheduler_id) is not None
                
    def start_auto_combat_skill(self):
        """
        Start auto cast skill.
        """
        # Cast a skill immediately
        # self.auto_cast_skill()

        # Set timer of auto cast.
        scheduler = self.get_scheduler()
        if scheduler.get_job(self.skill_scheduler_id):
            # auto cast job already exists
            return

        scheduler.add_job(self.auto_cast_skill, "interval", seconds=self.auto_cast_skill_cd, id=self.skill_scheduler_id)

    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        scheduler = self.get_scheduler()
        if not scheduler.get_job(self.skill_scheduler_id):
            # auto cast job already removed
            return

        scheduler.remove_job(self.skill_scheduler_id)


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

    async def attack_target(self, target, desc=""):
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
            logger.log_err("%s is already in battle." % self.get_id())
            return False

        # search target
        if not target:
            logger.log_err("Can not find the target.")
            return False

        if not target.is_element(SETTINGS.CHARACTER_ELEMENT_TYPE):
            # Target is not a character.
            logger.log_err("Can not attack the target %s." % target.get_id())
            return False

        if target.is_in_combat():
            # obj is already in battle
            logger.log_err("%s is already in battle." % target.get_id())
            return False

        # create a new combat handler
        try:
            await COMBAT_HANDLER.create_combat(
                combat_type=CombatType.NORMAL,
                teams={1: [target], 2: [self]},
                desc=desc,
                timeout=0
            )
        except Exception as e:
            logger.log_err("Can not create combat: [%s] %s" % (type(e).__name__, e))
            await self.msg({"alert": _("You can not attack %s.") % target.get_name()})

        return True

    async def attack_temp_target(self, target_key, target_level, desc=""):
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
        # Create a target.
        base_model = ELEMENT("CHARACTER").get_base_model()
        table_data = WorldData.get_table_data(base_model, key=target_key)
        if not table_data:
            logger.log_err("Can not create the target.")
            return False

        table_data = table_data[0]
        target = ELEMENT(table_data.element_type)()
        await target.setup_element(target_key, level=target_level, first_time=True, temp=True)
        if not target:
            logger.log_err("Can not create the target %s." % target_key)
            return False

        return await self.attack_target(target, desc)

    async def join_combat(self, combat_id):
        """
        The character joins a combat.

        :param combat_id: (int) combat's id.
        :return:
        """
        self.combat_id = combat_id

    def is_in_combat(self):
        """
        Check if the character is in combat.

        Returns:
            (boolean) is in combat or not
        """
        return self.combat_id is not None

    async def get_combat(self):
        """
        Get the character's combat. If the character is not in combat, return None.
        :return:
        """
        if not hasattr(self, "combat_id") or self.combat_id is None:
            return None

        combat = COMBAT_HANDLER.get_combat(self.combat_id)
        if combat is None:
            # Combat is finished.
            self.combat_id = None

        return combat

    async def combat_result(self, combat_type, result, opponents=None, rewards=None):
        """
        Set the combat result.

        :param combat_type: combat's type
        :param result: defines.COMBAT_WIN, defines.COMBAT_LOSE, or defines.COMBAT_DRAW
        :param opponents: combat opponents
        :param rewards: combat rewards
        """
        pass

    async def remove_from_combat(self):
        """
        Leave the current combat.
        """
        self.combat_id = None

    def is_player(self):
        """
        Check if this is a player character.

        :return:
        """
        return False

    def is_staff(self):
        """
        Check if this is a staff character.

        :return:
        """
        return False

    def bypass_events(self):
        """
        Check if this is a staff character.

        :return:
        """
        return False

    async def check_alive(self):
        """
        Check if the character is alive.
        :return:
        """
        self.is_alive = True
        return self.is_alive

    async def die(self, killers):
        """
        This character die.

        Args:
            killers: (list of objects) characters who kill this

        Returns:
            None
        """
        self.is_alive = False

        if not self.is_temp and self.reborn_time > 0:
            # Set reborn timer.
            reborn_time = datetime.utcfromtimestamp(time.time() + self.reborn_time)
            scheduler = self.get_scheduler()
            scheduler.add_job(self.reborn, "date", run_date=reborn_time, id=self.reborn_scheduler_id)

    async def reborn(self):
        """
        Reborn after being killed.
        """
        # Recover properties.
        await self.recover()
        self.is_alive = True

        # Reborn at its default location.
        location_key = self.const.location
        if location_key:
            try:
                home = Server.world.get_room(location_key)
                await self.move_to(home)
            except KeyError:
                pass

    async def recover(self):
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
        for key, skill in self.skills.items():
            if skill["obj"].is_passive():
                # exclude passive skills
                continue

            command = {
                "key": key,
                "name": skill["obj"].get_name(),
                "icon": skill["obj"].get_icon(),
            }

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

    async def add_exp(self, exp):
        """
        Add character's exp.
        Args:
            exp: the exp value to add.

        Returns:
            None
        """
        pass

    async def show_status(self):
        """
        Show character's status.
        """
        pass

    async def validate_property(self, key, value):
        """
        Check a property's value limit, return a validated value.

        Args:
            key: (string) values's key.
            value: (number) the value

        Return:
            (number) validated values.
        """
        # check limits
        max_value = None
        max_key = "max_" + key
        if await self.states.has(max_key):
            max_value = await self.states.load(max_key)
        elif self.const_data_handler.has(max_key):
            max_value = self.const_data_handler.get(max_key)

        if max_value is not None:
            if value > max_value:
                value = max_value

        min_value = 0
        min_key = "min_" + key
        if await self.states.has(min_key):
            min_value = await self.states.load(min_key)
        elif self.const_data_handler.has(min_key):
            min_value = self.const_data_handler.get(min_key)

        if value < min_value:
            value = min_value

        return value

    async def change_state(self, key, increment):
        """
        Change a state's value with validation.
        :return:
            the value that actually changed.
        """
        change = 0

        if await self.states.has(key):
            current_value = await self.states.load(key)
            new_value = await self.validate_property(key, current_value + increment)
            if new_value != current_value:
                change = new_value - current_value
                await self.states.save(key, new_value)

        return change

    async def change_states(self, increments):
        """
        Change a dict of states with validation.

        :return:
            the values that actually changed.
        """
        changes = {}
        state_values = {}

        for key, increment in increments.items():
            changes[key] = 0

            if await self.states.has(key):
                current_value = await self.states.load(key)
                new_value = await self.validate_property(key, current_value + increment)
                if new_value != current_value:
                    changes[key] = new_value - current_value
                    state_values[key] = new_value

        if state_values:
            await self.states.saves(state_values)

        return changes

    async def change_const_property(self, key, increment):
        """
        Change a const property with validation.
        :return:
            the value that actually changed.
        """
        change = 0

        if self.const_data_handler.has(key):
            current_value = self.const_data_handler.get(key)
            new_value = await self.validate_property(key, current_value + increment)
            change = new_value - current_value
            self.const_data_handler.add(key, new_value)

        return change

    async def change_const_properties(self, increments):
        """
        Change a dict of const properties with validation.

        :return:
            the values that actually changed.
        """
        changes = {}

        new_values = {}
        for key, increment in increments.items():
            changes[key] = 0

            if self.const_data_handler.has(key):
                current_value = self.const_data_handler.get(key)
                new_values[key] = current_value + increment

        # Get validated values
        if new_values:
            validated_values = await async_gather([self.validate_property(key, value) for key, value in new_values.items()])
            for index, key in enumerate(new_values):
                new_value = validated_values[index]
                changes[key] = new_value
                self.const_data_handler.add(key, new_value)

        return changes
