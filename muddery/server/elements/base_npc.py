"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.utils import logger
from muddery.server.utils.builder import build_object
from muddery.server.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.dao.npc_dialogues import NPCDialogues
from muddery.server.database.dao.npc_shops import NPCShops
from muddery.server.utils import defines
from muddery.server.utils.localized_strings_handler import _


class MudderyBaseNPC(ELEMENT("CHARACTER")):
    """
    The character not controlled by players.

    States:
        shops
    """
    element_key = "BASE_NPC"
    element_name = _("Base None Player Character", "elements")
    model_name = "base_npcs"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        super(MudderyBaseNPC, self).at_object_creation()

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyBaseNPC, self).after_data_loaded()

        # Character can auto fight.
        self.auto_fight = True

        # set home
        self.home = self.location

        # load dialogues.
        self.load_dialogues()

        # load shops
        self.load_shops()

    def load_dialogues(self):
        """
        Load dialogues.
        """
        dialogues = NPCDialogues.get(self.get_data_key())

        self.default_dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.dialogue and dialogue.default]
        self.dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.dialogue and not dialogue.default]

    def load_shops(self):
        """
        Load character's shop.
        """
        # shops records
        shop_records = NPCShops.get(self.get_data_key())
        shop_keys = set([record.shop for record in shop_records])

        # NPC's shop
        self.shops = self.states.load("shops", {})
        changed = False

        # remove old shops
        diff = set(self.shops.keys()) - shop_keys
        if len(diff) > 0:
            changed = True
            for shop_key in diff:
                # remove this shop
                self.shops[shop_key].delete()
                del self.shops[shop_key]

        # add new shops
        for shop_record in shop_records:
            shop_key = shop_record.shop
            if shop_key not in self.shops:
                # Create shop object.
                shop_obj = build_object(shop_key)
                if not shop_obj:
                    logger.log_errmsg("Can't create shop: %s" % shop_key)
                    continue

                self.shops[shop_key] = shop_obj
                changed = True

        if changed:
            self.states.save("shops", self.shops)

        # if the shop has no icon, set the NPC's icon to the shop.
        for key, obj in self.shops.items():
            if not obj.icon:
                obj.set_icon(self.icon)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            if self.dialogues or self.default_dialogues:
                # If the character have something to talk, add talk command.
                commands.append({"name": _("Talk"), "cmd": "talk", "args": self.dbref})

            # Add shops.
            for key, obj in self.shops.items():
                if not obj.is_visible(caller):
                    continue

                verb = obj.verb
                if not verb:
                    verb = obj.get_name()
                commands.append({"name": verb, "cmd": "shopping", "args": obj.dbref})

            if self.friendly <= 0:
                commands.append({"name": _("Attack"), "cmd": "attack", "args": self.dbref})

        return commands

    def have_quest(self, caller):
        """
        If the npc can complete or provide quests.
        Returns (can_provide_quest, can_complete_quest).
        """
        return DIALOGUE_HANDLER.have_quest(caller, self)

    def leave_combat(self):
        """
        Leave the current combat.
        """
        status = None
        opponents = None
        rewards = None
        if self.ndb.combat_handler:
            result = self.ndb.combat_handler.get_combat_result(self.id)
            if result:
                status, opponents, rewards = result

        if not self.is_temp:
            if status == defines.COMBAT_LOSE:
                self.die(opponents)

        super(MudderyBaseNPC, self).leave_combat()

        if not self.is_temp:
            if status != defines.COMBAT_LOSE:
                self.recover()
