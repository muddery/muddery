"""
This module defines constent constant values.
"""

# quest dependencies
DEPENDENCY_NONE = 0
DEPENDENCY_QUEST_CAN_PROVIDE = 1
DEPENDENCY_QUEST_ACCEPTED = 2
DEPENDENCY_QUEST_NOT_ACCEPTED = 3
DEPENDENCY_QUEST_IN_PROGRESS = 4
DEPENDENCY_QUEST_NOT_IN_PROGRESS = 5
DEPENDENCY_QUEST_ACHIEVED = 6           # quest achieved
DEPENDENCY_QUEST_NOT_ACHIEVED = 7       # quest accepted but not achieved
DEPENDENCY_QUEST_FINISHED = 8           # quest finished
DEPENDENCY_QUEST_NOT_FINISHED = 9       # quest not finished


# quest objective types
OBJECTIVE_NONE = 0
OBJECTIVE_TALK = 1      # object: dialogue_id
OBJECTIVE_ARRIVE = 2    # object: room_id
OBJECTIVE_OBJECT = 3    # object: object_id

# event trigger types
EVENT_TRIGGER_NONE = 0
EVENT_TRIGGER_ARRIVE = 1    # object: room_id
EVENT_TRIGGER_DIE = 2       # character die, object: killer_mob_id
EVENT_TRIGGER_KILL = 3      # kill a mob, object: mob_id

# event types
EVENT_NONE = 0
EVENT_ATTACK = 1        # event to begin a combat
EVENT_DIALOGUE = 2      # event to begin a dialogue