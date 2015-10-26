# Output Messages

In Muddery, all data send from the server to the client are strings in format of
```
CMD<JSON data>
```
It begins with `CMD` and follows JSON data. For example:
```
CMD{"login": {"dbref": "#16", "name": "USERNAME"}}
```

The keys of JSON data represent the message type. Available message types and data formats are as follows:


### msg
```
{"msg": "{RHello!{n My friend!"}
```
It is a common message with color tags. The client should translate these color tags to real color effect.


### err
```
{"err": <error_message>}
```
It is an error message.


### alert
```
{"alert": "{RWARNING!{n"}
```
or
```
{"alert": {"msg": <message>,
           "button": <text on the button>}
```
It can show a message with color tags on an alert window. In the second format, the data provide texts which can be show on the confirm button.


### login
```
{"login": {"name": <username>, "dbref": <player's dbref>}}
```
This message confirm the login of the player. After login, the server sends the username and the player's dbref to the client.


### puppet
```
{"puppet": <character's dbref>}
```
When a player puppets a character, usually right after the player login, this message will send the character's dbref to the client.


### logout
```
{"logout": ""}
```
This message confirm the logout of the player. When a player sends a logout command to the server and the server confirms the logout, this message will be sent to the client.


### status
```
{"status": {"attack": <value of attack>,
            "defence": <value of defence>,
            "level": <character's level>,
            "max_exp": <level's max exp>,
            "exp": <current exp>,
            "max_hp": <character's max hp>,
            "hp": <current hp>,
            "max_mp": <character's max mp>,
            "mp": <current mp>}}
```
These are character's attributes, include `hp`, `mp`, `exp` and other values. These data are sent to the client whenever the a player logs in or a character's attributes change.


### equipments
```
{"equipments": {<equipment_pos_1>: null,
                <equipment_pos_2>: {"dbref": <dbref>, "name": <name>, "desc": <desc>}}}
```
These are equipments that a character wears. Keys are positions. If there is an equipment on a position, the value is the equipment's `name`, `dbref` and `desc`. If there is no equipment, the value is `null`. <br>
These data are sent to the client whenever a player logs in or a character's equipments change.

### inventory
```
{"inventory": [{"name": <object's name>,
                "dbref": <object's dbref>,
                "number": <object's number>,
                "desc": <object's desc>,
                "equipped": <is equipped>}]}
```
This is a list of objects in character's inventory. Each item has object's `name`, `dbref`, `number` and `desc`.<br>
If the item is an equipment, it will has an additional attribute `equipped`. This attribute shows whether the equipment is equipped.


### skills
```
{"skills": [{"name": <skill's name>,
             "dbref": <skill's dbref>,
             "desc": <skill's desc>}]}
```
This is a list of skills that a character owns. Each item has skill's `name`, `dbref`, and `desc`.


### quests
```
{"quests": [{"name": <quest's name>,
             "dbref": <quest's dbref>,
             "desc": <quest's desc>,
             "objectives": [{"desc": <desc of an objective>}]}
```
or
```
{"quests": [{"name": <quest's name>,
             "dbref": <quest's dbref>,
             "desc": <quest's desc>,
             "objectives": [{"target": <objective's target>,
                             "object": <objective's object>,
                              "total": <target number>,
                              "achieved": <achieved number>}]}]}
```
`Quests` contains a list of quests that the character is doing. It has `name`, `dbref` and `desc`.<br>
The `objectives` is a list of quest objectives. The value can be the objective's desc or the objective's detail information.


### look_obj
```
{"look_obj": {"name": <object's name>,
              "desc": <object's desc>,
              "dbref": <object's dbref>,
              "cmds": [{"cmd": <command's key>,
                        "name": <command's name>,
                        "args": <command's args>}]}}
```
When a player send a `look` command to the server to looking at an object, the server will send back these data. These data is the object's appearance.<br>
`name` is the name of the object.<br>
`desc` is the description of the object.<br>
`dbref` is the dbref of the object.<br>
`cmds` is a list of commands that the player can do on the object.<br>
    `cmd` is the key of the command.<br>
    `name` is the name of the command to display.<br>
    `args` is the args of the command, usually is the dbref of the object.


### look_around
```
{"look_around": {"name": <room's name>,
                 "desc": <room's desc>,
                 "dbref": <room's dbref>,
                 "cmds": [<available commands>],
                 "exits": [{"name": <exit's name>, "dbref": <exit's dbref>}],
                 "things": [{"name": <thing's name>, "dbref": <thing's dbref>}],
                 "npcs": [{"name": <NPC's name>, "dbref": <NPC's dbref>}],
                 "players": [{"name": <player's name>, "dbref": <player's dbref>}]}}
```
When a player send a `look` command to the server to looking at his location, the server will send back these data. These data is the room's appearance and all objects that in this room.<br>
These data are similar to the `look_obj`, but the room has more data about other objects in it.<br>
`exits` are a list of exits.<br>
`things` are a list of common objects in the room.<br>
`npcs` are a list of NPCs in the room.<br>
`players` are online players in the room.<br>
Objects that does not match the condition will not be sent to the players.<br>
When a player login or moves into a room, these data will be sent to the player automatically.


### dialogue
```
{"dialogue": [{"content": <dialogues's words>,
               "speaker": <sperker's name>,
               "npc": <NPC's dbref>,
               "dialogue": <dialogue's key>,
               "sentence": <sentence's ordinal>}]}
```
When a player talk to an NPC or trigger a dialogues event, the server will send dialogue data to the client.<br>
It is a list of dialogues. If there are more than one dialogues, players can choose the one he want to say.<br>
`content` is the content of dialogue.<br>
`speaker` is the speaker's name.<br>
`dialogue` and `sentence` are used to locate the current sentence.<br>
If a player is talking to an NPC, `npc` is set to the NPC's dbref.


### get_object
```
{"get_object": {"accepted": {<object's name>: <object's number>},
                 "rejected": {<object's name>: <reject reason>}}}
```
It is the loot result, when a player uses a `loot` command.<br>
`accepted` is a list of accepted objects and their numbers.<br>
`rejected` is a list of rejected objects and their reasons.


### obj_moved_in
```
{"obj_moved_in": {<object's type>: [{"name": <object's name>,
                                     "dbref": <object's dbref>}]}}
```
The server sends this message to a player whenever any object moves into the player's location.<br>
`<object's type>` is the type of the object, it can be `exits`, `things`, `npcs`, or `players`.


### obj_moved_out
```
{"obj_moved_in": {<object's type>: [{"name": <object's name>,
                                     "dbref": <object's dbref>}]}}
```
The server sends this message to a player whenever any object moves out of the player's location.<br>
`<object's type>` is the type of the object, it can be `exits`, `things`, `npcs`, or `players`.


### player_online
```
{"player_online": {"name": <character's name>,
                   "dbref": <character's dbref>}
```
The server sends this message to a player whenever another player login into the same location.


### player_offline
```
{"player_offline": {"name": <character's name>,
                    "dbref": <character's dbref>}
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
{"combat_finish": {"winner": [{"name": <winner's name>,
                               "dbref": <winner's dbref>}]}}
```
The server sends this message to the client when a combat has finished. If there is no winner, the value is `{"stopped": True}`. If there are winners, sends a list of winner to the client.


### combat_info
```
{"combat_info": {"characters": [{"name": <character's name>,
                                 "dbref": <character's dbref>,
                                 "max_hp": <character's max hp>,
                                 "hp": <character's hp>}],
                 "desc": <combat's desc>}}
```
When a player joins a combat or looks at a combat, this message will be sent to the client.<br>
`characters` is a list of characters that in the combat.<br>
`desc` is the desc of the combat.


### combat_commands
```
{"combat_commands": [{"name": <command's name>,
                      "key": <command's key>}]}
```
When a player joins a combat or looks at a combat, this message will be sent to the client. It is a list of available commands.


### combat_process
```
{"combat_process": [{"type": "attacked",
                     "caller": <skill's caster>,
                     "target": <skill target's dbref>,
                     "hurt": <hurt of the target>,
                     "max_hp": <target's max hp>,
                     "hp": <target's hp>}]}
```
When a character in combat casts a skill, the result of the skill will be sent to the client.<br>
`caller` is the character who casts the skill.<br>
`target` is the target of the skill.<br>
`hurt`, `max_hp` and `hp` show the status change of the target.


### combat_skill_cd
```
{"combat_skill_cd": {"skill": <skill's key>,
                     "gcd": <GCD time>,
                     "cd": <skill CD time>}}
```
When a character in combat casts a skill, the cd of the skill will be sent to the client.<br>
`gcd` is global cd in seconds. In gcd, a character can not cast any skill.<br>
`cd` is skill's cd in seconds. In skill's cd, a character can not cast this skill.
