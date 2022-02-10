
from muddery.server.settings import SETTINGS
from muddery.common.utils.utils import class_from_path
from muddery.common.utils.defines import CombatType


class CombatHandler(object):
    """
    Create and store combats
    """

    def __init__(self):
        """
        All combats will be stopped when the server stops, so put combats in the memory.
        """
        self.combat_id = 0
        self.combats = {}

    async def create_combat(self, combat_type, teams, desc, timeout):
        """
        Create a new combat.

        :arg
            combat_type: (string) combat's type
            teams: (dict) {<team id>: [<characters>]}
            desc: (string) combat's description
            timeout: (int) Total combat time in seconds. Zero means no limit.
        """

        # Get new combat's id.
        new_combat_id = self.combat_id
        self.combat_id += 1

        if combat_type == CombatType.HONOUR:
            combat = class_from_path(SETTINGS.HONOUR_COMBAT_HANDLER)()
        else:
            combat = class_from_path(SETTINGS.NORMAL_COMBAT_HANDLER)()

        await combat.set_combat(self, new_combat_id, combat_type, teams, desc, timeout)
        combat.start()
        self.combats[new_combat_id] = combat

    def get_combat(self, combat_id):
        """
        Get a combat runner by its id.
        :param combat_id:
        :return:
        """
        return self.combats.get(combat_id, None)

    def remove_combat(self, combat_id):
        """
        Remove a combat by its id.

        :param combat_id:
        :return:
        """
        if combat_id in self.combats:
            del self.combats[combat_id]


COMBAT_HANDLER = CombatHandler()
