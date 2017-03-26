"""
This module defines available model types.
"""
from muddery.worlddata import data_settings as base


class BasicData(base.BasicData):
    pass


class ObjectsData(base.ObjectsData):
    pass


class ObjectsAdditionalData(base.ObjectsAdditionalData):
    pass


class OtherData(base.OtherData):
    pass


class EventAdditionalData(base.EventAdditionalData):
    pass
