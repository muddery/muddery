"""
The DialogueSet maintains a pool of dialogues.
"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.common.utils.singleton import Singleton


class DialogueSet(Singleton):
    """
    The DialogueSet maintains a pool of dialogues.
    """
    def __init__(self):
        """
        Initialize the handler.
        """
        super(DialogueSet, self).__init__()
        self.dialogue_storage = {}
    
    async def load_dialogue(self, dlg_key):
        """
        Load a dialogue data to the cache.
        """
        if not dlg_key:
            return

        if dlg_key in self.dialogue_storage:
            # already cached
            return

        # Add cache of the whole dialogue.
        dlg = ELEMENT("DIALOGUE")()
        await dlg.setup_element(dlg_key)
        self.dialogue_storage[dlg_key] = dlg

    def get_dialogue(self, dlg_key):
        """
        Get specified dialogue.

        Args:
            dlg_key (string): dialogue's key
        """
        if dlg_key not in self.dialogue_storage:
            # Can not find dialogue.
            return

        return self.dialogue_storage[dlg_key]

    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}
