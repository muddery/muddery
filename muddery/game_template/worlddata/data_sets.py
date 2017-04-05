"""
This module defines available model types.
"""

from __future__ import print_function

from muddery.worlddata.data_sets import DataSets as BaseDataSets
from muddery.worlddata.data_handler import DataHandler, SystemDataHandler, LocalizedStringsHandler


class DataSets(BaseDataSets):

    def at_creation(self):
        """
        You can add custom data handlers in this method.

        Returns:
            None
        """
        super(DataSets, self).at_creation()
        # self.add_data_handler(self.object_additional_data, DataHandler("custom_model"))
