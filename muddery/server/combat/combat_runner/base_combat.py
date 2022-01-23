"""
Combat handler.

The life of a combat:
1. create: create a combat.
2. set_combat: set teams in the combat and the end time if available, then calls the start_combat.
3. start_combat: start the combat. Characters in the combat are allowed to use skills.
4. prepare_skill: characters call the prepare_skill to use skills in the combat. It casts a skill and check if the
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
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from muddery.server.utils.logger import logger
from muddery.server.utils import defines
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET


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
                self.characters[character.get_id()] = {
                    "char": character,
                    "team": team,
                    "status":  CStatus.JOINED,
                }

        # Set combat to characters.
        for char in self.characters.values():
            character = char["char"]

            # add the combat handler
            await character.join_combat(combat_id)

            if character.is_player():
                await self.show_combat(character)

    def start(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        if self.timeout:
            # Set finish time.
            finish_time = datetime.datetime.fromtimestamp(time.time() + self.timeout)
            self.scheduler = AsyncIOScheduler()
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

    async def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        # Show combat information to the player.
        await character.msg([
            {
                "joined_combat": True
            },
            {
                "combat_info": self.get_appearance()
            },
            {
                "combat_status": await self.get_combat_status(),
            },
        ])

    async def prepare_skill(self, skill_key, caller, target_id):
        """
        Cast a skill.

        :arg
            skill_key: (string) skill's key
            caller: (obj) the skill's caller's object
            target_id: (int) target's id
        """
        if self.finished:
            return

        # get target's object
        target = None
        if target_id and target_id in self.characters:
            target = self.characters[target_id]["char"]

        if caller:
            await caller.cast_skill(skill_key, target)

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

        await asyncio.wait([
            asyncio.create_task(char["char"].check_alive())
            for char in self.characters.values() if char["status"] == CStatus.ACTIVE
        ])

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
            for char in self.characters.values():
                if char["status"] != CStatus.LEFT:
                    char["status"] = CStatus.LEFT
                    try:
                        await char["char"].remove_from_combat()
                    except Exception as e:
                        logger.log_err("Leave combat error: %s" % e)

            self.stop()

    async def msg_all(self, message):
        "Send message to all combatants"
        for char in self.characters.values():
            await char["char"].msg(message)

    async def set_combat_draw(self):
        """
        Called when the combat ended in a draw.

        Returns:
            None.
        """
        for char in self.characters.values():
            await char["char"].combat_result(self.combat_type, defines.COMBAT_DRAW)

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
        for winner_id, winner_char in winners.items():
            exp = 0
            loots = []
            for loser in losers:
                loser_char = self.characters[loser]["char"]
                exp += loser_char.provide_exp(self)
                obj_list = await loser_char.loot_handler.get_obj_list(winner_char)
                if obj_list:
                    loots.extend(obj_list)

            obj_list = []
            if loots:
                common_models = ELEMENT("COMMON_OBJECT").get_models()

                for obj_info in loots:
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
                "exp": exp,
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
        for char_id, char in winners.items():
            await char.combat_result(self.combat_type, defines.COMBAT_WIN, losers.values(), self.get_combat_rewards(char_id))

        for char_id, char in losers.items():
            await char.combat_result(self.combat_type, defines.COMBAT_LOSE, winners.values())

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

    async def get_combat_status(self):
        """
        Get characters status.
        :return:
        """
        chars = self.characters.keys()
        status = await asyncio.gather(*[char["char"].get_combat_status() for char in self.characters.values()])
        return dict(zip(chars, status))

    def get_combat_characters(self):
        """
        Get all characters in combat.
        """
        return self.characters.values()

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
