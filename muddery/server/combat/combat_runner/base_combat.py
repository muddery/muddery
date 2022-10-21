"""
Combat handler.

The life of a combat:
1. create: create a combat.
2. set_combat: set teams in the combat and the end time if available, then calls the start_combat.
3. start_combat: start the combat. Characters in the combat are allowed to use skills.
4. cast_skill: characters call the cast_skill to use skills in the combat. It casts a skill and check if the
   combat is finished.
5. can_finish: Check if the combat is finished. A combat finishes when only one or zero team has alive characters, or
   the combat is timeout. If a combat can finish calls the finish method.
6. finish: send combat results to all characters.
7. leave_combat: characters notify the combat that it has left.
8. stop: if all characters left, remove the combat.
"""

from enum import Enum
import time
import datetime
import pytz
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from muddery.common.utils.utils import async_wait, async_gather
from muddery.common.utils.exception import MudderyError, ERR
from muddery.common.utils import defines
from muddery.server.utils.logger import logger
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class CStatus(Enum):
    """
    Character's combat status.
    """
    JOINED = 1
    ACTIVE = 2
    FINISHED = 3
    ESCAPED = 4
    LEFT = 5


class BaseCombat(object):
    """
    This implements the combat handler.

    properties:
        characters: {
            "char_id": {
                "char": character's object,
                "team": team's id,
                "status": character's combat status,
            }
        }

    """
    # set initial values
    def __init__(self):
        self.characters = {}

        # if battle is finished
        self.finished = False
        self.winners = {}
        self.losers = {}

        # combat rewards
        self.rewards = {}

        self.timeout = 0
        self.scheduler = None

    def __del__(self):
        # When the combat is finished.
        if self.scheduler:
            self.scheduler.stop()

    async def at_timeout(self):
        """
        Combat timeout.

        Returns:
            None.
        """
        if self.finished:
            return

        await self.set_combat_draw()

    async def set_combat(self, handler, combat_id, combat_type, teams, desc, timeout):
        """
        Add combatant to handler

        Args:
            combat_id: (int) combat's id
            combat_type: (string) combat's type
            teams: (dict) {<team id>: [<characters>]}
            desc: (string) combat's description
            timeout: (int) Total combat time in seconds. Zero means no limit.
        """
        self.handler = handler
        self.combat_id = combat_id
        self.combat_type = combat_type
        self.desc = desc
        self.timeout = timeout

        # Add teams.
        for team in teams:
            for character in teams[team]:
                obj_id = character.get_id()
                self.characters[obj_id] = {
                    "char": character,
                    "team": team,
                    "status":  CStatus.JOINED,
                }

                try:
                    self.characters[obj_id]["db_id"] = character.get_db_id()
                except AttributeError:
                    self.characters[obj_id]["db_id"] = None

        # Set combat to characters.
        if self.characters:
            await async_wait([c["char"].join_combat(combat_id) for c in self.characters.values()])

    def start(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        if self.timeout:
            # Set finish time.
            finish_time = datetime.datetime.fromtimestamp(time.time() + self.timeout)
            self.scheduler = AsyncIOScheduler(timezone=pytz.utc)
            self.scheduler.add_job(self.at_timeout, "date", run_date=finish_time)
            self.scheduler.start()

        for char in self.characters.values():
            char["status"] = CStatus.ACTIVE

    def stop(self):
        """
        Stop this combat.
        :return:
        """
        self.handler.remove_combat(self.combat_id)

    async def cast_skill(self, skill_key, caller, target_id):
        """
        Cast a skill.

        :arg
            skill_key: (string) skill's key
            caller: (obj) the skill's caller's object
            target_id: (int) target's id

        :return
            {
                "skill_cd": skill's cd time,
                "result": cast_result,
            }
        """
        if self.finished:
            raise MudderyError(ERR.invalid_input, _("Combat finished."))

        if not caller:
            raise MudderyError(ERR.invalid_input, _("Can not cast the skill."))

        # get target's object
        target = None
        if target_id and target_id in self.characters:
            target = self.characters[target_id]["char"]

        result = await caller.cast_skill(skill_key, target)
        asyncio.create_task(self.msg_all({
            "combat_skill_cast": result["result"],
        }))
        asyncio.create_task(self.check_finish())

        return result

    async def check_finish(self):
        """
        Check the combat.
        """
        if await self.can_finish():
            # if there is only one team left, kill this handler
            await self.finish()

    async def can_finish(self):
        """
        Check if can finish this combat. The combat finishes when a team's members
        are all dead.

        Return True or False
        """
        if not len(self.characters):
            return False

        awaits = [c["char"].check_alive() for c in self.characters.values() if c["status"] == CStatus.ACTIVE]
        if awaits:
            await async_wait(awaits)

        teams = set()
        for char in self.characters.values():
            if char["status"] == CStatus.ACTIVE:
                if char["char"].is_alive:
                    teams.add(char["team"])
                    if len(teams) > 1:
                        # More than one team has alive characters.
                        return False

        return True

    async def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        self.finished = True

        if self.scheduler:
            self.scheduler.stop()
            self.scheduler = None

        # get winners and losers
        self.winners, self.losers = await self.calc_winners()

        for char in self.characters.values():
            char["status"] = CStatus.FINISHED

        # calculate combat rewards
        self.rewards = await self.calc_combat_rewards(self.winners, self.losers)

        await self.notify_combat_results(self.winners, self.losers)

    async def escape_combat(self, caller):
        """
        Character escaped.

        Args:
            caller: (object) the caller of the escape skill.

        Returns:
            None
        """
        if caller and caller.id in self.characters:
            self.characters[caller.id]["status"] = CStatus.ESCAPED
            await caller.combat_result(self.combat_type, defines.COMBAT_ESCAPED)

    async def leave_combat(self, character):
        """
        Remove combatant from handler.

        :param character: character object
        """
        if character.id in self.characters:
            if self.characters[character.id]["status"] == CStatus.LEFT:
                return
            self.characters[character.id]["status"] = CStatus.LEFT

        all_player_left = True
        for char in self.characters.values():
            if char["status"] != CStatus.LEFT and\
               char["char"].is_player():
                all_player_left = False
                break

        if all_player_left:
            # There is no player character in combat.
            awaits = []
            for char in self.characters.values():
                if char["status"] != CStatus.LEFT:
                    char["status"] = CStatus.LEFT
                    awaits.append(char["char"].remove_from_combat())

            if awaits:
                try:
                    await async_wait(awaits)
                except Exception as e:
                    logger.log_err("Leave combat error: %s" % e)

            self.stop()

    async def msg_all(self, message: dict) -> None:
        "Send message to all combatants."
        if self.characters:
            await async_wait([c["char"].msg(message) for c in self.characters.values()])

    async def set_combat_draw(self) -> None:
        """
        Called when the combat ended in a draw.

        Returns:
            None.
        """
        if self.characters:
            await async_wait([c["char"].combat_result(self.combat_type, defines.COMBAT_DRAW) for c in self.characters.values()])

    async def calc_winners(self):
        """
        Calculate combat winners and losers.
        """
        winner_team = None
        for char in self.characters.values():
            if char["status"] == CStatus.ACTIVE and char["char"].is_alive:
                winner_team = char["team"]
                break

        # winners and losers do not include escaped characters.
        winners = {char_id: char["char"] for char_id, char in self.characters.items()
                    if char["status"] == CStatus.ACTIVE and char["team"] == winner_team}
        losers = {char_id: char["char"] for char_id, char in self.characters.items()
                    if char["status"] == CStatus.ACTIVE and char["team"] != winner_team}
        return winners, losers

    async def calc_combat_rewards(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (dict) all combat winners.
            losers: (dict) all combat losers.

        Returns:
            (dict) reward dict
        """
        rewards = {}
        if not winners or not losers:
            return rewards

        exp_list = []
        loot_list = []
        for winner_id, winner_char in winners.items():
            # Get exps from every losers.
            exps = [self.characters[loser]["char"].provide_exp(self) for loser in losers]
            exp_list.append(exps)

            # Get loot tasks from every losers.
            loot_awaits = [self.characters[loser]["char"].loot_handler.get_obj_list(winner_char) for loser in losers]
            loot_list.append(loot_awaits)

        # Calculate all loots.
        loot_results = await async_gather([async_gather(char_loot) for char_loot in loot_list])

        common_models = ELEMENT("COMMON_OBJECT").get_models()

        for index, winner_id in enumerate(winners.keys()):
            obj_list = []
            for loot_list in loot_results[index]:
                for obj_info in loot_list:
                    try:
                        table_data = WorldData.get_tables_data(common_models, key=obj_info["object_key"])
                        table_data = table_data[0]

                        obj_list.append({
                            "object_key": obj_info["object_key"],
                            "level": obj_info["level"],
                            "number": obj_info["number"],
                            "name": table_data.name,
                            "icon": table_data.icon,
                            "reject": "",
                        })
                    except Exception as e:
                        logger.log_err("Can not loot object %s: %s." % (obj_info["object_key"], e))
                        pass

            rewards[winner_id] = {
                "exp": sum(exp_list[index]),
                "loots": obj_list,
            }

        return rewards

    def get_combat_rewards(self, char_id):
        """
        Get a character's combat rewards.
        """
        return self.rewards.get(char_id, None)

    async def notify_combat_results(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        winner_awaits = [char.combat_result(self.combat_type, defines.COMBAT_WIN, losers.values(), self.get_combat_rewards(char_id))
                         for char_id, char in winners.items()]
        loser_awaits = [char.combat_result(self.combat_type, defines.COMBAT_LOSE, winners.values())
                        for char_id, char in losers.items()]

        if winner_awaits or loser_awaits:
            await async_wait(winner_awaits + loser_awaits)

    def get_appearance(self):
        """
        Get the combat appearance.
        """
        characters = []
        for char in self.characters.values():
            character = char["char"]
            info = character.get_appearance()
            info["team"] = char["team"]

            characters.append(info)

        return {
            "desc": self.desc,
            "timeout": self.timeout,
            "characters": characters
        }

    async def get_combat_states(self):
        """
        Get characters states.
        :return:
        """
        if self.characters:
            chars = self.characters.keys()
            state = await async_gather([char["char"].get_combat_state() for char in self.characters.values()])
            return dict(zip(chars, state))
        else:
            return {}

    def get_combat_characters(self):
        """
        Get all characters in combat.
        """
        return self.characters.values()

    def get_character(self, db_id):
        """
        Get the character object by ist db_id.
        """
        for char_id, char_info in self.characters.items():
            if char_info["db_id"] == db_id:
                return char_info["char"]

    def get_opponents(self, character_id):
        """
        Get a character' opponents.
        :param character_id:
        :return:
        """
        if character_id not in self.characters:
            return []

        team = self.characters[character_id]["team"]

        # teammates = [c for c in characters if c.get_team() == team]
        opponents = [c["char"] for c in self.characters.values() if c["status"] == CStatus.ACTIVE and c["team"] != team]
        return opponents

    def is_finished(self):
        """
        :return: combat finished or not.
        """
        return self.finished

    def get_combat_type(self):
        """
        Get the combat's type.
        """
        return self.combat_type

    def get_combat_result(self, char_id):
        """
        Get a character's combat result.

        :param char_id: character's db id
        :return:
        """
        if not self.finished:
            return

        if char_id not in self.characters:
            return

        if self.characters[char_id]:
            status = self.characters[char_id]["status"]

            if status == CStatus.ESCAPED:
                return defines.COMBAT_ESCAPED, None, None
            elif status == CStatus.FINISHED or status == CStatus.LEFT:
                if char_id in self.winners:
                    return defines.COMBAT_WIN, self.losers.values(), self.get_combat_rewards(char_id)
                elif char_id in self.losers:
                    return defines.COMBAT_LOSE, self.winners.values(), None
                else:
                    return defines.COMBAT_DRAW, None, None
            else:
                return defines.COMBAT_DRAW, None, None
