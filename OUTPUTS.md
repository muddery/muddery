# Output Messages

In Muddery, all data send from the server to the client are strings in format of
```
CMD<JSON data>
```
It begins with 'CMD' and follows JSON data. For example:
```
CMD{"login": {"dbref": "#16", "name": "USERNAME"}}
```

The keys of JSON data represent the message type. Possible message types and data formats are as follows:


### msg
```
{"msg": "{RHello!{n My friend!"}
```
It is a common message with color tags. The client should translate these color tags to real color effect.


### err
```
{"err": <ERROR_MESSAGE>}
```
It sends an error message to the client.


### alert
```
{"alert": "{RWARNING!{n"}
```
or
```
{"alert": {"msg": <MESSAGE>,
           "button": <BUTTON_TEXT>}
```
It can show a message with color tags on an alert window. In the second format, the data provide texts which can be show on the confirm button.


### login
```
{"login": {"name": <USERNAME>, "dbref": <PLAYER_DBREF>}}
```
This message confirm the login of the player. When a player login, the server will send the username and the player's dbref to the client.


### puppet
```
{"puppet": <CHARACTER_DBREF>}
```
When a player puppets a character, usually right after the player login, this message will send the character's dbref to the client.


### logout
```
{"logout": ""}
```
This message confirm the logout of the player. When a player sends a logout command to the server and the server confirms the logout, this message will be sent to the client.


### status
```
{"status": {"attack": <ATTACK_VALUE>,
            "defence": <DEFENCE_VALUE>,
            "level": <CHARACTER_LEVEL>,
            "max_exp": <LEVEL_MAX_EXP>,
            "exp": <CURRENT_EXP>,
            "max_hp": <CHARACTER_MAX_HP>,
            "hp": <CURRENT_HP>,
            "max_mp": <CHARACTER_MAX_MP>,
            "mp": <CURRENT_MP>}}
```
These data send to the client whenever the character's data change or the player login. It includes `hp`, `mp`, `exp` and other attributes.


### equipments
```
{"equipments": {<EQUIPMENT_POS_1>: null,
                <EQUIPMENT_POS_2>: {"dbref": <DBREF>, "name": <NAME>, "desc": <DESC>}}}
```
These data send to the client whenever the character's equipments change or the player login.<br>
If there is no equipment on the position, the value will be set to `nil`. If there is an equipment, the value will be the equipment's `name`, `dbref` and `desc`.


### inventory
```
{"inventory": [{"name": <OBJ_NAME>,
                "dbref": <OBJ_DBREF>,
                "number": <OBJ_NUMBER>,
                "desc": <OBJ_DESC>,
                "equipped": <IS_EQUIPPED>}]}
```
`Inventory` contains a list of objects which are in your inventory. Each item has object's `name`, `dbref`, `number` and `desc`.<br>
If the item is an equipment, it will has an additional attribute `equipped`. This attribute shows whether the equipment is equipped.


### skills
```
{"skills": [{"name": <SKILL_NAME>,
             "dbref": <SKILL_DBREF>,
             "desc": <SKILL_DESC>}]}
```
`Skills` contains a list of skills that the character has. Each item has skill's `name`, `dbref`, and `desc`.


### quests
```
{"quests": [{"name": <QUEST_NAME>,
             "dbref": <QUEST_DBREF>,
             "desc": <QUEST_DESC>,
             "objectives": [{"desc": <OBJECTIVE_DESC>}]}
```
or
```
{"quests": [{"name": <QUEST_NAME>,
             "dbref": <QUEST_DBREF>,
             "desc": <QUEST_DESC>,
             "objectives": [{"target": <OBJECTIVE_TARGET>,
                             "object": <OBJECTIVE_OBJECT>,
                              "total": <TARGET_NUMBER>,
                              "achieved": <ACHIEVED_NUMBER>}]}]}
```
`Quests` contains a list of quests that the character is doing. It has `name`, `dbref` and `desc`.<br>
The `objectives` is a list of quest objectives. The value can be the objective's desc or the objective's detail information.


### look_obj
```
{"look_obj": {"name": <OBJ_NAME>,
              "desc": <OBJ_DESC>,
              "dbref": <OBJ_DBREF>,
              "cmds": [{"cmd": <COMMAND_KEY>,
                        "name": <COMMAND_NAME>,
                        "args": <COMMAND_ARGS>}]}}
```
When a player send a `look` command to the server to looking at an object, the server will send back these data. These data is the object's appearance.<br>
`name` is the name of the object that the player is looking at.<br>
`desc` is the description of the object that the player is looking at.<br>
`dbref` is the dbref of the object that the player is looking at.<br>
`cmds` is a list of commands that the player can do on the object.<br>
    `cmd` is the key of the command.<br>
    `name` is the name of the command to display.<br>
    `args` is the args of the command, usually is the dbref of the object.


### look_around
```
{"look_around": {"name": <ROOM_NAME>,
                 "desc": <ROOM_DESC>,
                 "dbref": <ROOM_DBREF>,
                 "cmds": [<AVAILABLE_COMMANDS>],
                 "exits": [{"name": <EXIT_NAME>, "dbref": <EXIT_DBREF>}],
                 "things": [{"name": <THING_NAME>, "dbref": <THING_DBREF>}],
                 "npcs": [{"name": <NPC_NAME>, "dbref": <NPC_DBREF>}],
                 "players": [{"name": <PLAYER_NAME>, "dbref": <PLAYER_DBREF>}],
                 "offlines": [{"name": <OFFLINE_PLAYER_NAME>, "dbref": <OFFLINE_PLAYER_DBREF>}]}}
```
When a player send a `look` command to the server to looking at a room, the server will send back these data. These data is the room's appearance and all objects that in this room.<br>
These data are similar to the `look`, but the room has more data about other objects in it.<br>
`exits` are a list of exits.<br>
`things` are a list of common objects in the room.<br>
`npcs` are a list of NPCs in the room.<br>
`players` are online players while `offlines` are offline players.<br>
This only return available objects to players. Objects that does not match the condition will not be sent to the players.<br>
When a player login or moves into a room, these data will be sent to the player automatically.


### dialogue
```
{"dialogue": [{"content": <DIALOGUE_WORDS>,
               "speaker": <SPEAKER_NAME>,
               "npc": <NPC_DBREF>,
               "dialogue": <DIALOGUE_KEY>,
               "sentence": <SENTENCE_ORDINAL>}]}
```
When a player talk to an NPC or trigger a dialogues event, the server will send dialogue data to the client.<br>
It is a list of dialogues. If there are more than one dialogues, players can choose the one he want to say.<br>
`content` is the content of dialogue.<br>
`speaker` is the speaker's name.<br>
`dialogue` and `sentence` are used to locate the current sentence.<br>
If a player is talking to an NPC, `npc` is set to the NPC's dbref.


### get_object
```
{"get_object": {"accepted": {<OBJ_NAME>: <OBJ_NUMBER>},
                 "rejected": {<OBJ_NAME>: <REJECT_REASON>}}}
```
It is the loot result, when a player uses a loot command.
`accepted` is a list of accepted objects and their numbers.
`rejected` is a list of rejected objects and their reasons.


### obj_moved_in
```
{"obj_moved_in": {<OBJ_TYPE>: [{"name": <OBJ_NAME>,
                                "dbref": <OBJ_DBREF>}]}}
```
The server sends this message to a player whenever any object moves into the player's location.<br>
`<OBJ_TYPE>` is the type of the object, it can be `exits`, `things`, `npcs`, or `players`.


### obj_moved_out
```
{"obj_moved_in": {<OBJ_TYPE>: [{"name": <OBJ_NAME>,
                                "dbref": <OBJ_DBREF>}]}}
```
The server sends this message to a player whenever any object moves out of the player's location.<br>
`<OBJ_TYPE>` is the type of the object, it can be `exits`, `things`, `npcs`, or `players`.


### player_online
```
{"player_online": {"name": <CHARACTER_NAME>,
                   "dbref": <CHARACTER_DBREF>}
```
The server sends this message to a player whenever another player login into the same location.


### player_offline
```
{"player_offline": {"name": <CHARACTER_NAME>,
                    "dbref": <CHARACTER_DBREF>}
```
The server sends this message to a player whenever another player in the same location logout.


### joined_combat
```
{"joined_combat": True}
```
The server sends this message to the client whenever the player joins a combat. The client should switch to combat mode at receiving this message.


### combat_finish
```
{"combat_finish": {"stopped": True}}
```
or
```
{"combat_finish": {"winner": [{"name": <WINNER_NAME>,
                               "dbref": <WINNER_DBREF>}]}}
```
The server sends this message to the client when a combat has finished. If there is no winner, the value is `{"stopped": True}`. If there are winners, sends a list of winner to the client.


### combat_info
```
{"combat_info": {"characters": [{"name": <CHARACTER_NAME>,
                                 "dbref": <CHARACTER_DBREF>,
                                 "max_hp": <CHARACTER_MAX_HP>,
                                 "hp": <CHARACTER_HP>}],
                 "desc": <COMBAT_DESC>}}
```
When a player joins a combat or looks at a combat, this message will be sent to the client.<br>
`characters` is a list of characters that in the combat.<br>
`desc` is the desc of the combat.


### combat_commands
```
{"combat_commands": [{"name": <COMMAND_NAME>,
                      "key": <COMMAND_KEY>}]}
```
When a player joins a combat or looks at a combat, this message will be sent to the client. It is a list of available commands.


### combat_process
```
{"combat_process": [{"type": "attacked",
                     "caller": <SKILL_CASTER>,
                     "target": <TARGET_DBREF>,
                     "hurt": <TARGET_HURT>,
                     "max_hp": <TARGET_MAX_HP>,
                     "hp": <TARGET_HP>}]}
```
When a character in combat casts a skill, the result of the skill will be sent to the client.<br>
`caller` is the character who casts the skill.<br>
`target` is the target of the skill.<br>
`hurt`, `max_hp` and `hp` show the status change of the target.


### combat_skill_cd
```
{"combat_skill_cd": {"skill": <SKILL_KEY>,
                     "gcd": <GCD_TIME>,
                     "cd": <CD_TIME>}}
```
When a character in combat casts a skill, the cd of the skill will be sent to the client.<br>
`gcd` is global cd. In gcd, a character can not cast any skill.<br>
`cd` is skill's cd. In skill's cd, a character can not cast this skill.
