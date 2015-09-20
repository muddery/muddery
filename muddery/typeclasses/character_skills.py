"""
skills

"""

import time
import traceback
from evennia import TICKER_HANDLER
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
                    self.db.owner.msg({"alert":LS("This skill is not ready yet!")})
                return

        try:
            result = self.cast()
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_info_key(), e)
            logger.log_errmsg(ostring)
            print traceback.format_exc()
            if self.db.owner:
                self.db.owner.msg({"alert":LS("Can not cast this skill!")})
            return

        return result


    def cast(self):
        """
        Do cast.
        """
        function = getattr(skills, self.get_info_key())
        result = function(self.db.owner, self.db.target, effect=self.effect)

        # reset cd
        if self.cd > 0:
            self.db.cd_end_time = time.time() + self.cd

        return result


    def set_auto_cast(self, target):
        """
        Start auto cast skill.
        """
        self.db.target = target
        reset_cd = self.cd_end_time - timt.time()

        if reset_cd < 0:
            reset_cd = 0
            
        TICKER_HANDLER.add(self, reset_cd, hook_key="at_auto_cast_cd")
        

    def stop_auto_cast(self, target):
        """
        Stop auto cast skill.
        """
        TICKER_HANDLER.remove(self)


    def at_auto_cast_cd(self, *args, **kwargs):
        """
        The first cd of the skill. It may be only a part of the whole cd.
        """
        TICKER_HANDLER.remove(self)
        
        try:
            self.cast()
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_info_key(), e)
            logger.log_errmsg(ostring)
            caller.msg({"alert":LS("Can not cast this skill!")})

        # set a new ticker
        TICKER_HANDLER.add(self, self.cd)


    def at_auto_cast(self, *args, **kwargs):
        """
        Auto cast skill.
        """
        try:
            self.cast()
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_info_key(), e)
            logger.log_errmsg(ostring)
            if self.db.owner:
                self.db.owner.msg({"alert":LS("Can not cast this skill!")})

            # stop ticker
            TICKER_HANDLER.remove(self, self.cd)
