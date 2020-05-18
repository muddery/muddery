"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class NPCDialogues(object):
    """
    NPC's dialogue list.
    """
    table_name = "npc_dialogues"

    @classmethod
    def get(cls, npc_key):
        """
        Get a NPC's dialogues.
        """
        return WorldData.get_table_data(cls.table_name, "npc", npc_key)
