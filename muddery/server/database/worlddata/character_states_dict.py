"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class CharacterStatesDict(BaseQuery):
    """
    Object properties dict.
    """
    table_name = "character_states_dict"
