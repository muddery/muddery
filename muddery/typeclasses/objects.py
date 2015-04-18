"""
AutoObj is an object which can load it's data automatically.

"""

from evennia import DefaultObject
from muddery.utils import loader


class MudderyObject(DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def at_init(self):
        """
        Load world data.
        """
        super(MudderyObject, self).at_init()
        
        # need save before modify m2m fields
        self.save()
        loader.load_data(self)
