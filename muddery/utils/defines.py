"""
This module defines constent constant values.
"""

# quest dependences
DEPENDENCE_NONE = 0
DEPENDENCE_QUEST_CAN_PROVIDE = 1
DEPENDENCE_QUEST_IN_PROGRESS = 2
DEPENDENCE_QUEST_NOT_IN_PROGRESS = 3
DEPENDENCE_QUEST_FINISHED = 4
DEPENDENCE_QUEST_UNFINISHED = 5
DEPENDENCE_QUEST_ACCEPTED = 6
DEPENDENCE_QUEST_NOT_ACCEPTED = 7

# quest objective types
OBJECTIVE_NONE = 0
OBJECTIVE_TALK = 1      # object: dialogue_id
OBJECTIVE_ARRIVE = 2    # object: room_id

# event trigger types
EVENT_TRIGGER_NONE = 0
EVENT_TRIGGER_ARRIVE = 1    # object: room_id
EVENT_TRIGGER_DIE = 2       # character die, object: killer_mob_id
EVENT_TRIGGER_KILL = 3      # kill a mob, object: mob_id

# event types
EVENT_NONE = 0
EVENT_ATTACK = 1
EVENT_DIALOGUE = 2