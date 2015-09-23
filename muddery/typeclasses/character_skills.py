"""
skills

"""

import time
import traceback
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from skills import skills


class MudderySkill(MudderyObject):
    """
    This is a skill.
    """
    
    def at_object_creation(self):
        """
        Set default values.
        """
        super(MudderySkill, self).at_object_creation()
        
        # set status
        self.db.owner = None
        self.db.target = None
        self.db.auto_cast = False
        self.db.cd_end_time = 0


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = [{"name":LS("CAST"), "cmd":"castskill", "args":self.get_info_key()}]
        return commands


    def set_owner(self, owner):
        """
        Set the owner of the skill.
        """
        self.db.owner = owner
    
        if self.passive:
            self.cast()
        else:
            if self.cd > 0:
                self.db.cd_end_time = time.time() + self.cd


    def cast_skill(self, target):
        """
        Cast this skill.
        """
        if self.passive:
            if self.db.owner:
                self.db.owner.msg({"alert":LS("You can not cast a passive skill.")})
            return

        self.db.target = target

        if self.cd > 0:
            if time.time() < self.db.cd_end_time:
                if self.db.owner:
                    self.db.owner.msg({"msg":LS("This skill is not ready yet!")})
                return

        try:
            function = getattr(skills, self.get_info_key())
            result = function(self.db.owner, self.db.target, effect=self.effect)

            # set cd
            if self.cd > 0:
                self.db.cd_end_time = time.time() + self.cd
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_info_key(), e)
            logger.log_errmsg(ostring)
            print traceback.format_exc()
            if self.db.owner:
                self.db.owner.msg({"msg":LS("Can not cast this skill!")})
            return

        return result


    def is_cooling_down(self):
        """
        If this skill is cooling down.
        """
        if self.cd > 0:
            if self.db.cd_end_time:
                if time.time() < self.db.cd_end_time:
                    return True
        return False
