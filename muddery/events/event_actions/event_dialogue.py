"""
Event action's base class.
"""

import muddery.events.base_event_action


class EventDialogue(BaseEventAction):
    """
    Event to start a combat.
    """
    key = "EVENT_DIALOGUE"

    def func(self, event, character):
        """
        Start a dialogue.
        """
        # Get sentence.
        npc = None
        if event["npc"]:
            npc = utils.search_obj_data_key(event["npc"])
            if npc:
                npc = npc[0]

        character.show_dialogue(npc, event["dialogue"], 0)
    
