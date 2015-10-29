# Database Tables

In Muddery, the whole game world is built by a series of tables. When the server starts up for the first time, the server will load these data and build the world. If you have modified some tables after the server start, you, as a builder, can use `@loadworld` command to rebuild the world and use `@reload` command to refresh data.

Here are main tables and example data. They are from our game example. You can use `muddery --init game_folder example` to install it.

## World Objects

World objects are unique in the world. We use `key` to identify them. If you add an object to these tables, this object will appear in the location you specified. If you remove an object from these tables, this object will be remove from the game world too.

### world_rooms
key | name | typeclass | desc
--- | --- | --- | ---
room_house | HOUSE | typeclasses.rooms.Room | This is a house.
room_cellar | CELLAR | typeclasses.rooms.Room | This is a cellar.
room_street | STREET | typeclasses.rooms.Room | This is a street.
room_dungeon | DUNGEON | typeclasses.rooms.Room | This is a dungeon.

Rooms are basic areas in the game. They build up the whole map of the game world together.<br>
`key` is the unique id of a room. This must be unique in all tables.<br>
`name` is the name of the room that shows to players.<br>
`typeclass` is the typeclass of the room.<br>
`desc` is the appearance of the room when players look at it.<br>

### world_exits
key | name | typeclass | desc | verb | location | destination
--- | --- | --- | --- | --- | --- | ---
exit_house_to_cellar | CELLAR | typeclasses.exits.Exit | Go to the cellar. | Go To | room_house | room_cellar
exit_cellar_to_house | HOUSE | typeclasses.exits.Exit | Leave the cellar. | Leave | room_cellar | room_house
exit_house_to_street | STREET | typeclasses.exits.Exit | Go to the street. | Go Out | room_house | room_street
exit_street_to_house | HOUSE | typeclasses.exits.Exit | Enter the house. | Enter | room_street | room_house
exit_street_to_dungeon | DUNGEON | typeclasses.exits.Exit | Go to the dungeon. | Go | room_street | room_dungeon
exit_dungeon_to_street | STREET | typeclasses.exits.Exit | Back to the street. | Back | room_dungeon | room_street

Characters must traverse exits to move from one room to another. Exits link rooms together. Exits are oneway, so if you want to move in and move out, you need to build two exits on each side.<br>
`key` is the unique id of an exit. This must be unique in all tables.<br>
`name` is the name of the exit that shows to players.<br>
`typeclass` is the typeclass of the exit.<br>
`desc` is the appearance of the exit when players look at it.<br>
`verb` is the name of the action of traverse. This shows to players to make the action looks better. If it is empty, the system will use a default verb.<br>
`location` is the room where the exit sets. The exit opens on this side. It must be a `key` in `world_rooms`.<br>
`destination` is the room where the exit leads to. It must be a `key` of `world_rooms`.<br>

### exit_locks
key | condition | verb | message_lock | auto_unlock
--- | --- | --- | --- | ---
exit_lock | have_object("obj_key") | UNLOCK | Use a key to unlock it. | 0

It is a special kind of exits. They are locked and players need to unlock it first to traverse it. Their appearance can be different after unlocked. These are additional data of `world_exits`.<br>
`key` is the `key` of an exit.<br>
`condition` is the condition of unlock. Players who matches the condition can unlock the exit. The condition's syntax will be explained in another document.<br>
`verb` is the name of the action of unlock. This shows to players to make the action looks better. If it is empty, the system will use a default verb.<br>
`message_lock` is the appearance of the exit when it is locked.<br>
`auto_unlock` If an exit is auto_unlock, players needn't do the unlock action, the exit can unlock itself automatically for players who match the condition.<br>

### world_objects
key | name | typeclass | desc | location | condition
--- | --- | --- | --- | --- | --- | ---
object_box | BOX | typeclasses.objects.Object | An empty box. | room_house |
creator_box | BOX | typeclasses.object_creators.ObjectCreator | A small box. | room_house |
creator_basket | BASKET | typeclasses.object_creators.ObjectCreator | A basket of apples. | room_house |
creator_bag | BAG | typeclasses.object_creators.ObjectCreator | A bag of potatoes. | room_cellar |
creator_rack | RACK | typeclasses.object_creators.ObjectCreator | This is a rack. | room_dungeon |

You can add objects to rooms by adding data to this table.<br>
`key` is the unique id of an object. This must be unique in all tables.<br>
`name` is the name of the object that shows to players.<br>
`typeclass` is the typeclass of the object.<br>
`desc` is the appearance of the object when players look at it.<br>
`location` is the room where the object stay. It must be a `key` in `world_rooms`.<br>
`condition` Players can only see objects that match the condition. The condition's syntax will be explained in another document.<br>

### object_creators
key | verb | loot_condition
--- | --- | ---
creator_box | SEARCH |
creator_basket | SEARCH | is_quest_in_progress("quest_apple")
creator_bag | SEARCH | is_quest_in_progress("quest_potato")
creator_rack | LOOT |

These are additional data for object creators.<br>
`key` is the `key` of an object creator.<br>
`verb` describes the action of loot that shows to players.<br>
`loot_condition` Players can only loot objects that match the condition. The condition's syntax will be explained in another document.<br>

### object_loot_list
provider | object | number | odds | condition
--- | --- | --- | --- | ---
creator_basket | obj_apple | 1 | 1 |
creator_bag | obj_potato | 1 | 1 |
creator_rack | equip_armor | 1 | 1 |
creator_rack | weapon_sword | 1 | 1 |

Object creators provide objects according to this loot list.<br>
`provider` is an object creator. It is a `key` in `object_creators`.<br>
`object` is the `key` of an common object that provided by this object creator. An object creator can provide several objects.<br>
`number` is the number of the objects provided.<br>
`odds` is the odds of the drop. It is a float number between 0 to 1.<br>
`condition` is the condition of the drop. Players can only get objects that match the condition. The condition's syntax will be explained in another document.<br>

### world_npcs
key | name | typeclass | desc | location | condition
--- | --- | --- | --- | --- | --- | ---
npc_boy | BOY | typeclasses.npcs.NPC | This is a boy. | room_street |

You can add NPCs by adding data to this table.<br>
`key` is the unique id of an NPC. This must be unique in all tables.<br>
`name` is the name of the NPC that shows to players.<br>
`typeclass` is the typeclass of the NPC.<br>
`desc` is the appearance of the NPC when players look at it.<br>
`location` is the room where the NPC stay. It must be a `key` in `world_rooms`.<br>
`condition` Players can only see NPCs that match the condition. The condition's syntax will be explained in another document.<br>

## Common Objects

Common objects are not unique in the game world. There can be a lot of common objects of have the same `key`.

### common_objects
key | name | typeclass | desc | max_stack | unique | effect | action
--- | --- | --- | --- | --- | --- | --- | --- | ---
obj_apple | APPLE | typeclasses.common_objects.CommonObject | An apple. | 10 | 0 | 0 | 
obj_potato | POTATO | typeclasses.common_objects.CommonObject | A potato. | 10 | 0 | 0 | 

Common objects are objects that players can put them into their inventories.<br>
`key` is the unique id of an object. This must be unique in all tables.<br>
`name` is the name of the object that shows to players.<br>
`typeclass` is the typeclass of the object.<br>
`desc` is the appearance of the object when players look at it.<br>
`max_stack` limits the max number of objects in a pile. For example, if the `max_stack` of apples is 10, the max number of a pile of apples is 10. If you have 11 apples, they will be divided into 2 piles.<br>
`unique` determines whether players can have more than one pile of this object. `0` means `NO` and `1` means `YES`.<br>
`effect` is a float value that can provide as an argument when players use this object.<br>
`action` is a short script that runs when players use this object. The action's syntax will be explained in another document.<br>
It does not have `location` field because common objects can appear everywhere.<br>

### common_characters
key | name | typeclass | desc
--- | --- | --- | ---
mob_rogue | ROGUE | typeclasses.monsters.Monster | This is a rogue. He is dangerous.

Common characters are characters that can appear everywhere.<br>
`key` is the unique id of a character. This must be unique in all tables.<br>
`name` is the name of the character that shows to players.<br>
`typeclass` is the typeclass of the character.<br>
`desc` is the appearance of the character when players look at it.<br>

## Quests

Quests are special objects stored in characters. One quest object represents a quest. It can have several objectives. There are a series of tables work for the quest system.

### quests
key | name | typeclass | desc | condition | action
--- | --- | --- | --- | --- | --- 
quest_apple | APPLE | typeclasses.character_quests.Quest | Find an apple. | |
quest_potato | POTATO | typeclasses.character_quests.Quest | Find a potato. | |

Quests are objects stored in characters.
`key` is the unique id of a quest. This must be unique in all tables.<br>
`name` is the name of the quest that shows to players.<br>
`typeclass` is the typeclass of the quest.<br>
`desc` is the appearance of the quest when players look at it.<br>
`condition` Players can only accept quests that match the condition. The condition's syntax will be explained in another document.<br>
`action` is a short script that runs when players finish a quest. The action's syntax will be explained in another document.<br>

### quest_objectives
quest | ordinal | type | object | number | desc
--- | --- | --- | --- | --- | --- 
quest_apple | 1 | 3 | obj_apple | 1 | Find an apple.
quest_potato | 1 | 3 | obj_potato | 1 |

`quest_objectives` are objectives of quests. A quest can have several objectives. A quest is achieved while all its objectives are achieved.<br>
`quest` is the `key` of the quest that have this objective.<br>
`ordinal` is the ordinal number of an objective. `quest` and `ordinal` together must be unique.<br>
`type` is the type of the objective, such as `getting some objects`, `talking to somebody`, or `arriving some place`. They are defined in `units/defines.py`.<br>

### quest_dependency
quest | dependency | type
--- | --- | ---
quest_potato | quest_apple | 8

This table sets the dependencies of quests. A quest is available while all its dependencies are matched.<br>
`quest` is the key of the quest that have this objective.<br>
`dependency` is this quest's dependent quest. It is the `key` of another quest.<br>
`type` is the dependency's type. They are defined in `units/defines.py`.<br>

## Dialogues
Dialogues are basic units of a talk. They can have branches, so players can choose what they want to say. Dialogues also have conditions, so an NPC can talk different things to players. A dialogue has several sentences which are indivisible. A dialogue can only start from the first sentence.

### dialugues
key | condition
--- | ---
dlg_hello |
dlg_apple | 
dlg_potato |
dlg_event |

This table has all dialogues' key and their conditions.<br>
`key` is the key of the dialogues. It must be unique in this table.<br>
`condition` Players can only see dialugues that match the condition. The condition's syntax will be explained in another document.<br>

### dialogue_sentences
dialogue | ordinal | speaker | content | action | provide_quest | finish_quest
--- | --- | --- | --- | --- | --- | ---
dlg_hello | 1 | n | Hello! | | |
dlg_apple | 1 | n | Can you find me an apple? | | |
dlg_apple | 2 | p | OK! | | quest_apple |
dlg_potato | 1 | n | Can you find me a potato? | | |
dlg_potato | 2 | p | OK! | | quest_potato |
dlg_event | 1 | "voice" | Welcome! | | |

A dialogues can have several sentences, but a dialogue must begin from the first sentence. If a dialogue is interrupted, players can not continue from the middle of the dialogue. They must start from the beginning.<br>
Sentence can provide and/or finish quests.<br>
`dialogue` is the `key` of a dialogue.<br>
`ordinal` is the ordinal of the sentence. `dialogue` and `ordinal` together must be unique.<br>
`speaker` is the name of speaker that players can see. If it is `p`, the speaker's name will be the name of the player. If it is `n`, the speaker's name will be the name of the NPC. If it is a string quoted in `"`, the speaker's name will be the string in the quotes. Otherwise it will be empty.<br>
`content` is the texts of the sentence.<br>
`action` is a short script that runs when players use this sentence. The action's syntax will be explained in another document.<br>
`provide_quest` is the `key` of a quest. When players use sentences with `provide_quest`, they will accept this quest if they can.<br>
`finish_quest` is the `key` of a quest. When players use sentences with `finish_quest`, they will finish this quest if they can.<br>

### dialogue_relations
dialogue | next
--- | ---
dlg_apple | dlg_potato

A dialogue can leads to one or several dialogues. If there several dialogues, players can choose the one that they want say.<br>
`dialogue` is the `key` of a dialogue.<br>
`next` is another dialogue's `key` which this dialogue leads to.<br>

### dialogue_quest_dependency
dialogue | dependency | type
--- | --- | ---
dlg_apple | quest_apple | 1
dlg_no_apple | quest_apple | 7
dlg_has_apple | quest_apple | 6
dlg_potato | quest_potato | 1
dlg_potato | quest_apple | 8
dlg_no_potato | quest_potato | 7
dlg_has_potato | quest_potato | 6

This table sets the dependencies of quests. A dialogue is available while all its dependencies are matched.<br>
`dialogue` is the `key` of a dialogue.<br>
`dependency` is this dialogue's dependent quest. It is the `key` of a quest.<br>
`type` is the dependency's type. They are defined in `units/defines.py`.<br>

### npc_dialogues
npc | dialogue | default
--- | --- | ---
npc_boy | dlg_hello | 1
npc_boy | dlg_apple | 
npc_boy | dlg_potato |

You can add dialogues to NPCs by adding data to this table.<br>
`npc` is the `key` of an NPC.<br>
`dialogue` is the `key` of a dialogue.<br>
`default` is whether this dialogue is default or not. `0` means `NO` and `1` means `YES`. If an NPC can show non-default dialogues, it will not show default dialogues. Default dialogues can only be shown when other dialogues are not available.<br>

## Events
Player's actions can trigger events, such as moving into a special room or killing a special NPC. The event can lead to a dialogue or begin a fight.

### event_data
key | trigger | object | type | condition
--- | --- | --- | --- | ---
event_dialogue | 1 | room_cellar | 2 |
event_fight | 1 | room_dungeon | 1

All events are in this table.<br>
`key` is the unique id of an event. It must be unique in this table.<br>
`trigger` is how the event can be triggered. It can be arriving, killing or other types. They are defined in `units/defines.py`.<br>
`object` is the object's `key` of the trigger target. For example, if the `trigger` is arriving a room, the `object` is the `key` of the room.<br>
`type` is the type of the event. It can be a dialogue or a fight. They are defined in `units/defines.py`.<br>
`condition` is the condition of the event. The condition's syntax will be explained in another document.<br>

### event_dialogues
key | dialogue | npc
--- | --- | ---
event_dialogue | dlg_event | 

These data are used to create dialogues in events.<br>
`key` is the `key` of an event.<br>
`dialogue` is the `key` of the dialogue that will be triggered.<br>
`npc` is the `key` of an NPC. If it is not empty, the NPC speaker's name will be this NPC's name. If it is empty, the NPC speaker's name will be empty.<br>

### event_mobs
key | mob | level | odds | desc
--- | --- | --- | --- | ---
event_fight | mob_rogue | 1 | 1 | A rogue is attacking you!

It is the data of how events trigger fights.<br>
`key` is the `key` of an event.<br>
`mob` is the `key` of the mob that will attack players.<br>
`level` is the level of the mob.<br>
`odds` is the odds of the event. It is a float number between 0 to 1.<br>
`desc` is the description of this fight. It will show to players.<br>

## character's data

These data are character's attributes and skills.

### character_level
character | level | max_exp | max_hp | max_mp | attack | defence
--- | --- | --- | --- | --- | --- | ---
player | 1 | 100 | 100 | 100 | 10 | 10
player | 2 | 120 | 120 | 100 | 12 | 12
player | 3 | 150 | 150 | 100 | 15 | 15
npc_boy | 1 | 1 | 1 | 1 | 1 | 1
mob_rogue | 1 | 20 | 20 | 100 | 5 | 5

Character's attribute can increase with level up.<br>
`character` is the `key` of the character. If it is a player, the key should be `DEFAULT_PLAYER_CHARACTER_KEY` in `settings.py`.<br>
`level` is the level of a character.<br>
`max_exp`, `max_hp`, `max_mp`, `attack` and `defence` are character's attributes.<br>

### skills
key | name | typeclass | desc | cd | passive | condition | function | effect
--- | --- | --- | --- | --- | --- | --- | --- | ---
skill_hit | HIT | typeclasses.character_skills.Skill | Hit an enemy. | 1 | 0 | | skill_hit | 1

Character's skills are special objects. When a player casts a skill, the skill object calls a skill function. Skill function model's position is defined by `SKILL_FOLDER` and `SKILL_FILES` in `settings.py`. If a skill casted successfully, the result of the skill and the CD will be sent to the client.<br>
`key` is the unique id of a skill. This must be unique in all tables.<br>
`name` is the name of the skill that shows to players.<br>
`typeclass` is the typeclass of the skill.<br>
`desc` is the description of the skill.<br>
`cd` is the cool down time in seconds.<br>
`passive` is whether the skill is passive or not. `0` means `NO` and `1` means `YES`. If it is a passive skill, players can not cast it manually.<br>
`condition` is the condition of the skill. Players can only cast skills that match the condition. The condition's syntax will be explained in another document.<br>
`function` is the name of the skill function. The function must be defined in skill models. Skill function model's position is defined by `SKILL_FOLDER` and `SKILL_FILES` in `settings.py`.<br>
`effect` is a float value that can provide as an argument when players cast this skill.<br>

### character_skill
character | skill
--- | ---
player | skill_hit
mob_rogue | skill_hit

Characters can have default skills. All default skills are in this table.<br>
`character` is the `key` of a character. If it is a player, the key should be `DEFAULT_PLAYER_CHARACTER_KEY` in `settings.py`.<br>
`skill` is the `key` of a skill.<br>

## Equipments

Player characters can wear equipments to increase their attributes. Every equipment has its position. Equipments can only be put on their positions. Every equipment has a type too. This type relates to character's career. Equipments can only be put on characters with right career. 

### equipments
key | name | typeclass | desc | max_stack | unique | position | type | attack | defence
--- | --- | --- | --- | --- | --- | --- | --- | --- | ---
equip_armor | ARMOR | typeclasses.common_objects.Equipment | This is an armor. | 1 | 1 | chest | plate | | 10
weapon_sword | SWORD | typeclasses.common_objects.Equipment | This is a sword. | 1 | 1 | hand | weapon | 10 |

`key` is the unique id of an equipment. This must be unique in all tables.<br>
`name` is the name of the equipment that shows to players.<br>
`typeclass` is the typeclass of the equipment.<br>
`desc` is the appearance of the equipment when players look at it.<br>
`max_stack` limits the max number of equipments in a pile. It is the same as the `max_stack` in common_objects.<br>
`unique` determines whether players can have more than one pile of this equipment. It is the same as the `unique` in common_objects.<br>
`position` is the position to wear. Positions are defined by `EQUIP_POSITIONS` in `settings.py`.<br>
`type` is the type of the equipment.<br>
`attack` and `defence` are attributes add to characters.<br>

### equipment_types
type | name | career
--- | --- | ---
plate | PLATE |
weapon | WEAPON |

This table describes the relations between equipment types and character careers. A type can relate to several careers.<br>
`type` is the key of the equipment type.<br>
`name` is the name of the equipment type that shows to players.<br>
`career` is the related career. If it is empty, equipments of this type can be put on every kind of characters.<br>
