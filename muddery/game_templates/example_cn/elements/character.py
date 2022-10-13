"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import traceback
from muddery.server.elements.character import MudderyCharacter


class Character(MudderyCharacter):
    """
    Custom character class.

    """
    element_type = "CHARACTER"

    async def recover(self):
        """
        Recover properties.
        """
        await super(Character, self).recover()
        
        # Recover hp and mp.
        values = {
            "hp": self.const.max_hp,
            "mp": self.const.max_mp
        }
        await self.states.saves(values)
        
    async def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        await super(Character, self).level_up()

        # Recover hp and mp.
        await self.recover()

    async def get_combat_state(self):
        """
        Get character status used in combats.
        """
        state = await super(Character, self).get_combat_state()

        state["max_hp"] = self.const.max_hp
        state["hp"] = await self.states.load("hp")
        state["max_mp"] = self.const.max_mp
        state["mp"] = await self.states.load("mp")

        return state

    async def check_alive(self):
        """
        Check if the character is alive.

        Returns:
            (boolean) the character is alive or not
        """
        self.is_alive = round(await self.states.load("hp")) > 0
        return self.is_alive

    def provide_exp(self, killer):
        """
        Calculate the exp provide to the killer.
        Args:
            killer: (object) the character who kills it.

        Returns:
            (int) experience give to the killer
        """
        return self.const.give_exp

    async def add_exp(self, exp):
        """
        Add character's exp.
        Args:
            exp: the exp value to add.

        Returns:
            None
        """
        await super(Character, self).add_exp(exp)

        results = {}
        current_exp = await self.states.load("exp")
        new_exp = current_exp + exp
        while new_exp >= self.const.max_exp:
            if self.const.max_exp > 0:
                # can upgrade
                new_exp -= self.const.max_exp
                await self.level_up()
                results["level_up"] = self.get_level()
            else:
                # can not upgrade
                new_exp = 0
                break

        if new_exp != current_exp:
            await self.states.save("exp", new_exp)

        return results
