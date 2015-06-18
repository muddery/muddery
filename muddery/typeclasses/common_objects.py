"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject

class CommonObject(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def load_data(self):
        """
            Set data_info to the object."
            """
        super(CommonObject, self).load_data()
        
        data = self.get_data_record()
        if not data:
            return
        
        # set common object's info
        self.max_stack = data.max_stack
        self.unique = data.unique
        self.action = data.action
        
        # set total number
        self.db.number = 0


    def at_init(self):
        """
        Load world data.
        """
        super(CommonObject, self).at_init()

        # need save before modify m2m fields
        self.save()

        try:
            self.load_data()
        except Exception, e:
            logger.log_errmsg("%s can not load data:%s" % (self.dbref, e))


    def get_number(self):
        """
        Get object's number.
        """
        return self.db.number


    def increase_num(self, number):
        """
        Increase object's number.
        """
        if number == 0:
            return
        
        if number < 0:
            raise MudderyError("%s can not increase a negative nubmer." % key)
            return

        if self.max_stack == 1 and self.db.number == 1:
            raise MudderyError("%s can not stack." % key)
            return

        if self.db.number + number > self.max_stack:
            raise MudderyError("%s over stack." % key)
            return
        
        self.db.number += number
        return


    def decrease_num(self, number):
        """
        Decrease object's number.
        """
        if number == 0:
            return

        if number < 0:
            raise MudderyError("%s can not decrease a negative nubmer." % key)
            return

        if self.db.number < number:
            raise MudderyError("%s's number below zero." % key)
            return
        
        self.db.number -= number
        return

