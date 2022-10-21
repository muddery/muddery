"""
This model translates default strings into localized strings.
"""
from collections import deque
import time
import datetime
import math
import pytz
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.database.gamedata.honours_mapper import HonoursMapper
from muddery.server.utils.localized_strings_handler import _
from muddery.common.utils.defines import CombatType
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.server import Server
from muddery.common.utils.singleton import Singleton
from muddery.common.utils.utils import async_wait


class MatchPVPHandler(Singleton):
    """
    This model translates default strings into localized strings.
    """
    def __init__(self):
        """
        Initialize handler
        """
        super(MatchPVPHandler, self).__init__()
        
        self.max_honour_diff = 0
        self.preparing_time = 0
        self.match_interval = 10

        # waiting_queue: a list of character's db id
        self.waiting_queue = deque()

        # preparing:
        #   character's db id: {
        #       "time": begin time,
        #       "opponent": match's opponent,
        #       "confirmed": confirmed the combat,
        #       "job_id": waiting caller's id,
        #   }
        self.preparing = {}

        self.scheduler = AsyncIOScheduler(timezone=pytz.utc)
        self.loop = None
        self.key = "MATCH_PVP_HANDLER"

        self.reset()
        
    def __del__(self):
        """
        Clear all resources.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

        self.remove_all()

    def remove_all(self):
        """
        # Remove all characters in the waiting queue.
        """
        for char_db_id, info in self.preparing.values():
            job_id = info["job_id"]
            self.scheduler.remove_job(job_id)

            try:
                character = Server.world.get_character(char_db_id)
                character.msg({"match_rejected": None})
            except Exception:
                pass

        self.preparing.clear()

        for char_db_id in self.waiting_queue:
            try:
                character = Server.world.get_character(char_db_id)
                character.msg({"left_combat_queue": True})
            except Exception:
                pass

        self.waiting_queue.clear()

    def reset(self):
        """
        Reset the waiting queue.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

        # Remove all characters in the waiting queue.
        self.remove_all()

        honour_settings = HonourSettings.get_first_data()
        if honour_settings:
            self.max_honour_diff = honour_settings.max_honour_diff
            self.preparing_time = honour_settings.preparing_time
            self.match_interval = honour_settings.match_interval

        # add the loot job
        if self.scheduler.get_job(self.key) is None:
            self.scheduler.add_job(self.match, "interval", seconds=self.match_interval, id=self.key)
            self.scheduler.start()

    async def add(self, character):
        """
        Add a character to the queue.
        """
        char_db_id = character.get_db_id()

        if char_db_id in self.waiting_queue:
            raise MudderyError(ERR.invalid_input, _("You are already in the queue."))
        
        self.waiting_queue.append(char_db_id)

    async def remove(self, character):
        """
        Remove a character from the queue.
        """
        char_db_id = character.get_db_id()

        try:
            self.waiting_queue.remove(char_db_id)
        except ValueError:
            pass

        try:
            del self.preparing[char_db_id]
        except KeyError:
            pass

    async def match(self):
        """
        Match opponents according to character's scores.
        The longer a character in the queue, the score is higher.
        The nearer of two characters' rank, the score is higher.
        """
        if len(self.waiting_queue) < 2:
            return

        # match characters by honour differences
        for i in range(len(self.waiting_queue) - 1):
            char_id_A = self.waiting_queue[i]
            if char_id_A in self.preparing:
                continue

            for j in range(i + 1, len(self.waiting_queue)):
                char_id_B = self.waiting_queue[j]
                if char_id_B in self.preparing:
                    continue

                honour_A = HonoursMapper.inst().get_honour(char_id_A, 0)
                honour_B = HonoursMapper.inst().get_honour(char_id_B, 0)

                # max_honour_diff means no limits
                if self.max_honour_diff == 0 or math.fabs(honour_A - honour_B) <= self.max_honour_diff:
                    # can match
                    awaits = []
                    try:
                        character_A = Server.world.get_character(char_id_A)
                        awaits.append(character_A.msg({"prepare_match": self.preparing_time}))
                    except KeyError:
                        pass

                    try:
                        character_B = Server.world.get_character(char_id_B)
                        awaits.append(character_B.msg({"prepare_match": self.preparing_time}))
                    except KeyError:
                        pass

                    if awaits:
                        await async_wait(awaits)

                    job_time = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(seconds=self.preparing_time)
                    job = self.scheduler.add_job(self.fight, 'date', run_date=job_time, args=(char_id_A, char_id_B))

                    self.preparing[char_id_A] = {
                        "time": time.time(),
                        "opponent": char_id_B,
                        "confirmed": False,
                        "job_id": job.id,
                    }
                    self.preparing[char_id_B] = {
                        "time": time.time(),
                        "opponent": char_id_A,
                        "confirmed": False,
                        "job_id": job.id,
                    }

    def confirm(self, character):
        """
        Confirm an honour combat.
        """
        char_db_id = character.get_db_id()

        try:
            self.preparing[char_db_id]["confirmed"] = True
        except KeyError:
            pass

    async def reject(self, character):
        """
        Reject an honour combat.
        """
        char_db_id = character.get_db_id()
        try:
            info = self.preparing[char_db_id]
        except KeyError:
            return

        # stop the call
        job_id = info["job_id"]
        self.scheduler.remove_job(job_id)
        
        # remove characters from the preparing queue
        del self.preparing[char_db_id]

        opponent_db_id = info["opponent"]
        try:
            del self.preparing[opponent_db_id]
        except KeyError:
            pass

        try:
            opponent = Server.world.get_character(opponent_db_id)
            asyncio.create_task(opponent.msg({"match_rejected": character.get_id()}))
        except KeyError:
            pass

        await self.remove(character)

    async def fight(self, char_id_A, char_id_B):
        """
        Create a combat.
        """
        def remove_by_id(char_db_id):
            """
            Remove a character from the queue.
            """
            try:
                self.waiting_queue.remove(char_db_id)
            except ValueError:
                pass

            try:
                del self.preparing[char_db_id]
            except KeyError:
                pass

        confirmed_A = char_id_A in self.preparing and self.preparing[char_id_A]["confirmed"]
        confirmed_B = char_id_B in self.preparing and self.preparing[char_id_B]["confirmed"]

        if not confirmed_A and not confirmed_B:
            # Neither characters is confirmed.
            remove_by_id(char_id_A)
            remove_by_id(char_id_B)

            awaits = []
            try:
                character0 = Server.world.get_character(char_id_A)
                awaits.append(character0.msg({"match_rejected": character0.get_id()}))
            except KeyError:
                pass

            try:
                character1 = Server.world.get_character(char_id_B)
                awaits.append(character1.msg({"match_rejected": character1.get_id()}))
            except KeyError:
                pass

            if awaits:
                await async_wait(awaits)

        elif not confirmed_A:
            # Opponents 0 not confirmed.

            # Remove opponent 0.
            remove_by_id(char_id_A)

            awaits = []
            try:
                character0 = Server.world.get_character(char_id_A)
                awaits.append(character0.msg({"match_rejected": character0.get_id()}))
            except KeyError:
                pass

            # Put opponent 1 back to the waiting queue.
            try:
                del self.preparing[char_id_B]
            except KeyError:
                pass

            try:
                character1 = Server.world.get_character(char_id_B)
                awaits.append(character1.msg({"match_rejected": None}))
            except KeyError:
                pass

            if awaits:
                await async_wait(awaits)

        elif not confirmed_B:
            # opponents 1 not confirmed

            # Remove opponent 1.
            remove_by_id(char_id_B)

            awaits = []
            try:
                character0 = Server.world.get_character(char_id_B)
                awaits.append(character0.msg({"match_rejected": character0.get_id()}))
            except KeyError:
                pass

            # Put opponent 0 back to the waiting queue.
            try:
                del self.preparing[char_id_A]
            except KeyError:
                pass

            try:
                character1 = Server.world.get_character(char_id_A)
                awaits.append(character1.msg({"match_rejected": None}))
            except KeyError:
                pass

        elif confirmed_A and confirmed_B:
            # all confirmed

            # create a combat
            opponent0 = Server.world.get_character(char_id_A)
            opponent1 = Server.world.get_character(char_id_B)

            # create a new combat
            combat = await COMBAT_HANDLER.create_combat(
                combat_type=CombatType.HONOUR,
                teams={1:[opponent0], 2:[opponent1]},
                desc=_("Fight of Honour"),
                timeout=0
            )

            remove_by_id(char_id_A)
            remove_by_id(char_id_B)

            combat_data_0 = {
                "combat_info": combat.get_appearance(),
                "combat_commands": opponent0.get_combat_commands(),
                "combat_states": await combat.get_combat_states(),
                "from": opponent0.get_name(),
                "target": opponent1.get_name(),
            }

            combat_data_1 = {
                "combat_info": combat.get_appearance(),
                "combat_commands": opponent1.get_combat_commands(),
                "combat_states": await combat.get_combat_states(),
                "from": opponent1.get_name(),
                "target": opponent0.get_name(),
            }

            await async_wait([
                opponent0.msg({"honour_combat": combat_data_0}),
                opponent1.msg({"honour_combat": combat_data_1}),
            ])
