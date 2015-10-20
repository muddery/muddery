# Database Tables

In muddery, the whole game world is build on a series of tables. When the server starts up for the first time, the server will load these data and build the world. If you have modified some tables after the server start, you, as a builder, can use `@loadworld` command to rebuild the world and use `@reload` command to refresh data.

## World Objects

World objects are unique in the world. We use `key` to identify them. If you add an object to these tables, this object will appear in the location you specified. If you remove an object from these tables, this object will be remove from the game world too.

### world_rooms
key | name | typeclass | desc
--- | --- | --- | ---
room_house | HOUSE | typeclasses.rooms.Room | This is a house.
room_kitchen | KITCHEN | typeclasses.rooms.Room | This is a kitchen.
room_street | STREET | typeclasses.rooms.Room | This is a street.

Rooms are basic areas in the game. They build up the whole map of the game world.<br>
`key` is the unique id of the room. This must be unique in all tables.<br>
`name` is the name of the room that shows to players.<br>
`typeclass` is the typeclass of the room.<br>
`desc` is the appearance of the room when players look at it.

### world_exits
key | name | typeclass | desc | verb | location | destination
--- | --- | --- | --- | --- | --- | ---
exit_house_to_kitchen | DOOR | typeclasses.exits.Exit | Go to the kitchen. | Go To | room_house | room_kitchen
exit_kitchen_to_house | DOOR | typeclasses.exits.Exit | Leave the kitchen. | Leave | room_kitchen | room_house
exit_house_to_street | DOOR | typeclasses.exits.Exit | Go to the street. | Go Out | room_house | room_street
exit_street_to_house | DOOR | typeclasses.exits.Exit | Enter the house. | Enter | room_street | room_house

Characters must traverse exits to move from one room to another. Exits link rooms together. Exits are oneway, so if you want to move in and move out, you need to build two exits on each side.<br>
`key` is the unique id of the exit. This must be unique in all tables.<br>
`name` is the name of the exit that shows to players.<br>
`typeclass` is the typeclass of the exit.<br>
`desc` is the appearance of the exit when players look at it.<br>
`verb` is the name of the action of traverse. This shows to players to make the action looks better. If it is empty, the system will use a default verb.<br>
`location` is the room where the exit sets. The exit opens on this side. It must be a key of world_rooms.<br>
`destination` is the room where the exit leads to. It must be a key of world_rooms.

### world_objects
key | name | typeclass | desc | location | condition
--- | --- | --- | --- | --- | --- | ---
object_box | BOX | typeclasses.objects.Object | An empty box. | room_house

You can add objects to rooms in this way. Player can see these objects and use them if they have relative commands.<br>
`key` is the unique id of the object. This must be unique in all tables.<br>
`name` is the name of the object that shows to players.<br>
`typeclass` is the typeclass of the object.<br>
`desc` is the appearance of the object when players look at it.<br>
`location` is the room where the object stay.<br>
`condition` Players only can see objects that match the condition. The condition's syntax will be explained in another document.

### object_creators
key | name | typeclass | desc | location | condition | verb
creator_basket | BASKET | typeclasses.object_creators.ObjectCreator | This basket is full of apples. | | PICK
creator_bag | BAG | typeclasses.object_creators.ObjectCreator | This bag is full of potato. | | PICK

`object_creators` inherits from `world_objects`, so its fields is similare to `world_objects`.<br>
It has one more field `verb`, it discribs the action of loot and will show to players.

### world_npcs
key | name | typeclass | desc | location | condition
--- | --- | --- | --- | --- | --- | ---
npc_boy | BOY | typeclasses.npcs.NPC | room_street | This is a boy. | 

You can add NPCs in this way.<br>
`key` is the unique id of the NPC. This must be unique in all tables.<br>
`name` is the name of the NPC that shows to players.<br>
`typeclass` is the typeclass of the NPC.<br>
`desc` is the appearance of the NPC when players look at it.<br>
`location` is the room where the NPC stay.<br>
`condition` Players only can see NPCs that match the condition. The condition's syntax will be explained in another document.

## Common Objects

Common objects are not unique in the game world. There can be a lot of common objects of have the same key.

### common_objects
key | name | typeclass | desc | max_stack | unique | effect | action
--- | --- | --- | --- | --- | --- | --- | --- | ---
obj_apple | APPLE | typeclasses.common_objects.CommonObject | An apple. | 10 | 0 | 0 | 
obj_potato | POTATO | typeclasses.common_objects.CommonObject | A potato. | 10 | 0 | 0 | 

Common objects are objects that players can put them into their inventories.<br>
`key` is the unique id of the object. This must be unique in all tables.<br>
`name` is the name of the object that shows to players.<br>
`typeclass` is the typeclass of the object.<br>
`desc` is the appearance of the object when players look at it.<br>
`max_stack` limits the max number of objects in a pile. For example, if the `max_stack` of apples is 10, the max number of a pile of apples is 10. If you have 11 apples, they will be divided into 2 piles. 
`unique` determines whether players can have more than one pile of this object. `0` means `NO` and `1` means `YES`.
`effect` is a float value that can provide as an argument when players use this object.
`action` is a short script that runs when players use this object. The action's syntax will be explained in another document.
It does not have `location` field because common objects can appear everywhere. 

### common_characters
key | name | typeclass | desc
--- | --- | --- | ---
mob_rogue | ROGUE | typeclasses.monsters.Monster | This is a rogue. He is dangerous.

Common characters are characters that can appear everywhere.<br>
`key` is the unique id of the character. This must be unique in all tables.<br>
`name` is the name of the character that shows to players.<br>
`typeclass` is the typeclass of the character.<br>
`desc` is the appearance of the character when players look at it.<br>

## Quests

Quests are special objects stored in characters. One quest object represents a quest. It can have several objectives. There are a series of tables work for the quest system.

### quests
key | name | typeclass | desc | condition | action
--- | --- | --- | --- | --- | --- 
quest_apple | APPLE | typeclasses.character_quests.Quest | Get an apple. | |
quest_potato | POTATO | typeclasses.character_quests.Quest | Get a potato. | |

Quests are objects stored in characters.
`key` is the unique id of the quest. This must be unique in all tables.<br>
`name` is the name of the quest that shows to players.<br>
`typeclass` is the typeclass of the quest.<br>
`desc` is the appearance of the quest when players look at it.<br>
`condition` Players only can accept quests that match the condition. The condition's syntax will be explained in another document.<br>
`action` is a short script that runs when players finish a quest. The action's syntax will be explained in another document.

### quest_objectives
quest | ordinal | type | object | number | desc
--- | --- | --- | --- | --- | --- 
quest_apple | 1 | 3 | obj_apple | 1 | Get an apple.
quest_potato | 1 | 3 | obj_potato | 1 |

`quest_objectives` are objectives of quests. A quest can have several objectives. A quest is achieved when its objectives are all achieved.
`quest` is the key of the quest that have this objective.
`ordinal` is the ordinal number of an objective. `quest` and `ordinal` together must be unique.
`type` is the type of the objective, such as `getting some objects`, `talking to somebody`, or `arriving some place`. They are defined in `units/defines.py`.

### quest_dependency
quest | dependency | type
--- | --- | ---
quest_potato | quest_apple | 8

This table sets the dependencies of quests. A quest is available with all its dependencies matched.<br>
`quest` is the key of the quest that have this objective.<br>
`dependency` is this quest's dependency.
`type` is the dependency's type. They are defined in `units/defines.py`.

