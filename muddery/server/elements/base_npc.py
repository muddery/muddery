"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.common.utils import defines
from muddery.common.utils.utils import async_wait, async_gather
from muddery.server.utils.logger import logger
from muddery.server.mappings.dialogue_set import DialogueSet
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.npc_dialogues import NPCDialogues
from muddery.server.database.worlddata.npc_shops import NPCShops
from muddery.server.database.worlddata.worlddata import WorldData

from muddery.server.utils.localized_strings_handler import _

from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class MudderyBaseNPC(ELEMENT("CHARACTER")):
    """
    The character not controlled by players.

    States:
        shops
    """
    element_type = "BASE_NPC"
    element_name = "Base None Player Character"
    model_name = ""

    def __init__(self, *agrs, **wargs):
        super(MudderyBaseNPC, self).__init__(*agrs, **wargs)

        self.auto_fight = True
        self.dialogues = []
        self.shops = {}

    async def at_element_setup(self, first_time):
        """
        Init the character.
        """
        await super(MudderyBaseNPC, self).at_element_setup(first_time)

        # Character can auto fight.
        self.auto_fight = True

        # load dialogues.
        await self.load_dialogues()

        # load shops
        await self.load_shops()

    async def load_dialogues(self):
        """
        Load dialogues.
        """
        records = NPCDialogues.get(self.get_element_key())
        if records:
            self.dialogues = [{
                "key": record.dialogue,
                "condition": record.condition,
                "otherwise": record.otherwise,
            } for record in records]
            await async_wait([DialogueSet.inst().load_dialogue(r.dialogue) for r in records])

    async def get_dialogues(self, caller):
        """
        Get NPC's dialogues that can show to the caller.

        Args:
            caller: (object) the character who want to start a talk.

        Returns:
            dialogues: (list) a list of available dialogues.
        """
        if not caller:
            return

        dialogues = []

        # Get the NPC's dialogues.
        if self.dialogues:
            candidates = [item for item in self.dialogues if not item["otherwise"]]
            if candidates:
                matches = await async_gather([STATEMENT_HANDLER.match_condition(item["condition"], caller, self)
                                              for item in candidates])
                dialogues = [DialogueSet.inst().get_dialogue(item["key"]) for index, item in enumerate(candidates)
                             if matches[index]]

                if not dialogues:
                    # Get otherwise sentences.
                    dialogues = [DialogueSet.inst().get_dialogue(item["key"]) for item in self.dialogues
                                 if item["otherwise"]]

        dialogues = [{"key": d.get_element_key(), "content": d.get_content()} for d in dialogues]

        return {
            "target": {
                "id": self.get_id(),
                "name": self.get_name(),
                "icon": getattr(self, "icon", None),
            },
            "dialogues": dialogues,
        }

    async def load_shops(self):
        """
        Load character's shop.
        """
        # shops records
        shop_records = NPCShops.get(self.get_element_key())
        shop_keys = set([record.shop for record in shop_records])
        base_model = ELEMENT("SHOP").get_base_model()

        # NPC's shop
        if shop_keys:
            shops = await async_gather([self.create_shop(base_model, key) for key in shop_keys])
            self.shops = dict(zip(shop_keys, shops))

    async def create_shop(self, base_model, shop_key):
        """
        Create a shop.
        """
        try:
            table_data = WorldData.get_table_data(base_model, key=shop_key)
            table_data = table_data[0]

            shop = ELEMENT(table_data.element_type)()
            await shop.setup_element(shop_key)
            shop.set_owner(self)
        except Exception as e:
            logger.log_trace("Can not create shop %s: (%s)%s" % (shop_key, type(e).__name__, e))
            return

        return shop

    async def get_shop_info(self, shop_key, caller):
        """
        Show shop's information to the player.
        :param shop_key:
        :param caller:
        :return:
        """
        if shop_key not in self.shops:
            return None

        shop_info = await self.shops[shop_key].get_detail_appearance(caller)
        shop_info["npc"] = self.get_id()
        return shop_info

    async def sell_goods(self, shop_key, goods_index, caller):
        """
        Sell goods to the caller.
        :param shop_key:
        :param goods_index:
        :param caller:
        :return:
        """
        if shop_key not in self.shops:
            return None

        return await self.shops[shop_key].sell_goods(goods_index, caller)

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive:
            relationship = await caller.get_relationship(self.element_type, self.get_element_key())
            if relationship is None:
                # Use the default relationship.
                relationship = self.default_relationship

            if self.dialogues or self.default_dialogues:
                # If the character have something to talk, add talk command.
                commands.append({"name": _("Talk"), "cmd": "talk", "args": self.get_id()})

            if relationship <= 0:
                commands.append({"name": _("Attack"), "cmd": "attack", "args": self.get_id()})

            if relationship >= 0:
                # Add shops.
                if self.shops:
                    available_shops = await async_gather([obj.is_available(caller) for obj in self.shops.values()])
                    for index, key in enumerate(self.shops.keys()):
                        if not available_shops[index]:
                            continue

                        obj = self.shops[key]
                        verb = obj.get_verb()
                        commands.append({
                            "name": verb,
                            "cmd": "shopping",
                            "args": {
                                "npc": self.get_id(),
                                "shop": obj.get_element_key(),
                            }
                        })

        return commands

    async def remove_from_combat(self):
        """
        Removed from the current combat.
        """
        status = None
        opponents = None
        rewards = None

        combat = await self.get_combat()
        if combat:
            result = combat.get_combat_result(self.id)
            if result:
                status, opponents, rewards = result

        if not self.is_temp:
            if status == defines.COMBAT_LOSE:
                await self.die(opponents)

        await super(MudderyBaseNPC, self).remove_from_combat()

        if not self.is_temp:
            if status != defines.COMBAT_LOSE:
                await self.recover()
