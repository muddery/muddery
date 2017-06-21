"""
MudderyNPC is NPC's base class.

"""

import json
import traceback
from evennia import TICKER_HANDLER
from evennia.utils import logger
from muddery.typeclasses.characters import MudderyCharacter
from muddery.utils.localized_strings_handler import _
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.builder import build_object, delete_object
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS


class MudderyNPC(MudderyCharacter):
    """
    Default NPC. NPCs are friendly to players, they can not be attacked.
    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyNPC, self).at_object_creation()
        
        # NPC's shop
        if not self.attributes.has("shops"):
            self.db.shops = {}

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyNPC, self).after_data_loaded()

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
        npc_key = self.get_data_key()
        dialogues = DATA_SETS.npc_dialogues.objects.filter(npc=npc_key)

        self.default_dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.default]
        self.dialogues = [dialogue.dialogue for dialogue in dialogues if not dialogue.default]

    def load_shops(self):
        """
        Load character's shop.
        """
        # shops records
        shop_records = DATA_SETS.npc_shops.objects.filter(npc=self.get_data_key())

        shop_keys = set([record.shop for record in shop_records])

        # remove old shops
        for shop_key in self.db.shops:
            if shop_key not in shop_keys:
                # remove this shop
                self.db.shops[shop_key].delete()
                del self.db.shops[shop_key]

        # add new shop
        for shop_record in shop_records:
            shop_key = shop_record.shop
            if shop_key not in self.db.shops:
                # Create shop object.
                shop_obj = build_object(shop_key)
                if not shop_obj:
                    logger.log_errmsg("Can't create shop: %s" % shop_key)
                    continue

                self.db.shops[shop_key] = shop_obj
                
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.dialogues or self.default_dialogues:
            # If the character have something to talk, add talk command.
            commands.append({"name":_("Talk"), "cmd":"talk", "args":self.dbref})
        
        # Add shops.
        for shop_obj in self.db.shops.values():
            if not shop_obj.is_visible(caller):
                continue

            verb = shop_obj.verb
            if not verb:
                verb = shop_obj.get_name()
            commands.append({"name":verb, "cmd":"shopping", "args":shop_obj.dbref})
        
        return commands

    def have_quest(self, caller):
        """
        If the npc can complete or provide quests.
        Returns (can_provide_quest, can_complete_quest).
        """
        return DIALOGUE_HANDLER.have_quest(caller, self)
