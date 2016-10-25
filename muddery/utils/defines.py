"""
This module defines constent constant values.
"""

# quest dependencies
DEPENDENCY_NONE = ""
DEPENDENCY_QUEST_CAN_PROVIDE = "DPD_CAN_PROVIDE"
DEPENDENCY_QUEST_ACCEPTED = "DPD_ACCEPTED"
DEPENDENCY_QUEST_NOT_ACCEPTED = "DPD_NOT_ACCEPTED"
DEPENDENCY_QUEST_IN_PROGRESS = "DPD_IN_PROGRESS"
DEPENDENCY_QUEST_NOT_IN_PROGRESS = "DPD_NOT_IN_PROGRESS"
DEPENDENCY_QUEST_ACCOMPLISHED = "DPD_ACCOMPLISHED"          # quest accomplished
DEPENDENCY_QUEST_NOT_ACCOMPLISHED = "DPD_NOT_ACCOMPLISHED"  # quest accepted but not accomplished
DEPENDENCY_QUEST_COMPLETED = "DPD_COMPLETED"                # quest complete
DEPENDENCY_QUEST_NOT_COMPLETED = "DPD_NOT_COMPLETED"        # quest accepted but not complete

# quest objective types
OBJECTIVE_NONE = ""
OBJECTIVE_TALK = "OBJECTIVE_TALK"           # finish a dialogue, object: dialogue_id
OBJECTIVE_ARRIVE = "OBJECTIVE_ARRIVE"       # arrive a room, object: room_id
OBJECTIVE_OBJECT = "OBJECTIVE_OBJECT"       # get some objects, object: object_id
OBJECTIVE_KILL = "OBJECTIVE_KILL"           # kill some characters, object: character_id

# event trigger types
EVENT_TRIGGER_NONE = 0
EVENT_TRIGGER_ARRIVE = "EVENT_TRIGGER_ARRIVE"       # at attriving a room. object: room_id
EVENT_TRIGGER_KILL = "EVENT_TRIGGER_KILL"           # caller kills one. object: dead_one_id
EVENT_TRIGGER_DIE = "EVENT_TRIGGER_DIE"             # caller die. object: killer_id
EVENT_TRIGGER_TRAVERSE = "EVENT_TRIGGER_TRAVERSE"   # before traverse an exit. object: exit_id

# event types
EVENT_NONE = ""
EVENT_ATTACK = "EVENT_ATTACK"               # event to begin a combat
EVENT_DIALOGUE = "EVENT_DIALOGUE"           # event to begin a dialogue