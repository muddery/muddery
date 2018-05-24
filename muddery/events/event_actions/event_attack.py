"""
Event action's base class.
"""

import muddery.events.base_event_action


class EventAttack(BaseEventAction):
    """
    Event to start a combat.
    """
    key = "EVENT_ATTACK"

    def func(self, event, character):
        """
        Start a combat.
        """
        rand = random.random()

        # If matches the odds, put the character in combat.
        # There can be several mods with different odds.
        if rand <= event["odds"]:
            # Attack mob.
            character.attack_temp_target(event["mob"], event["level"], event["desc"])
    
