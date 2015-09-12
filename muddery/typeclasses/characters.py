"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.objects import MudderyObject
from muddery.typeclasses.common_objects import MudderyEquipment
from evennia.objects.objects import DefaultCharacter
from evennia.utils import logger
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.quest_handler import QuestHandler
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from evennia.utils.utils import lazy_property


class MudderyCharacter(MudderyObject, DefaultCharacter):
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

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()
        
        self.db.level = 1
        self.db.exp = 0

        self.db.hp = 1
        self.db.mp = 1
        
        self.max_hp = 1
        self.max_mp = 1
        
        self.attack = 0
        self.defence = 0

        equipments = {}
        for position in settings.EQUIP_POSITIONS:
            equipments[position] = None
        self.db.equipments = equipments
        
        self.db.skills = {}
        
        # set quests
        self.db.finished_quests = set()
        self.db.current_quests = {}

        self.set_init_data()


    def at_init(self):
        """
        called whenever typeclass is cached from memory,
        at least once every server restart/reload
        """
        super(MudderyCharacter, self).at_init()

        self.set_init_data()


    def set_init_data(self):
        """
        Load initial data.
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
        self.after_equipment_changed()


    def use_object(self, obj):
        """
        Use an object.
        """
        pass


    def after_equipment_changed(self):
        """
        Called after equipments changed. It's time to calculate character's attributes.
        """

        # set level informations
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.CHARACTER_LEVELS)
            level_data = model_obj.objects.get(level=self.db.level)

            known_fields = set(["level"])
            for field in level_data._meta.fields:
                if field.name in known_fields:
                    continue
                if field.name in self.reserved_fields:
                    print "Can not set reserved field %s!" % field.name
                    continue
                setattr(self, field.name, level_data.serializable_value(field.name))

        except Exception, e:
            print "Can't load character level info %s: %s" % (self.db.level, e)

        # find equipments
        equipped = set()
        equipments = self.db.equipments
        for position in equipments:
            if equipments[position]:
                equipped.add(equipments[position])

        # add equipment's attributes
        for content in self.contents:
            if content.dbref in equipped:
                for effect in settings.EQUIP_EFFECTS:
                    value = getattr(self, effect, 0)
                    value += getattr(content, effect, 0)
                    setattr(self, effect, value)


    def has_skill(self, skill):
        """
        Whether the character has the skill.
        args:
            skill: (string) The key of the skill.
        """
        return skill in self.db.skills


    def cast_skill(self, skill, target):
        """
        Cast a skill.
        """
        if not skill in self.db.skills:
            self.msg({"alert":LS("You do not have this skill.")})
            return

        return self.db.skills[skill].cast_skill(target)


    def is_in_combat(self):
        """
        """
        return bool(self.ndb.combat_handler)


    def hurt(self, damage):
        """
        """
        self.db.hp -= damage
        if self.db.hp < 0:
            self.db.hp = 0

        if self.db.hp <= 0:
            self.die()

        return


    def die(self):
        """
        """
        pass


    def is_alive(self):
        """
        """
        return self.db.hp > 0


    def get_combat_commands(self):
        """
        This returns a list of combat commands.
        """
        commands = []
        for key in self.db.skills:
            skill = self.db.skills[key]
            command = {"name": skill.name,
                       "key": skill.get_info_key()}
            commands.append(command)
        return commands
