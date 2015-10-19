Output Messages
===

In Muddery, all data sent from the server to the client are strings in format of
```
CMD<JSON data>
```
It begins with 'CMD' and follows a string of JSON data. For example:
```
CMD{"login": {"dbref": "#16", "name": "USERNAME"}}
```

The key of JSON data represents the data type. Possible data type and data format are as follows:

# msg
```
{"msg": "{RHello!{n My friend!"}
```
It is a common message with color tags. The client should translate these color tags to real color effect.


# alert
```
{"alert": "{RWARNING!{n"}
```
or
```
{"alert": {"msg": "<MESSAGE>",
		   "button": "<BUTTON>"}
```
It can show a message with color tags on an alert window. In the second format, the data provide texts which can be show on the confirm button.


# login
```
{"login": {"name": "<USERNAME>", "dbref": "<PLAYER_DBREF>"}}
```
This message confirm the login of the player. When a player login, the server will send the username and the player's dbref to the client.


# puppet
```
{"puppet": "<CHARACTER_DBREF>"}
```
When a player puppets a character, usually right after the player login, this message will send the character's dbref to the client.


# logout
```
{"logout": ""}
```
This message confirm the logout of the player. When a player sends a logout command to the server and the server confirms the logout, this message will be sent to the client.


# status
```
{"status": {"attack": 10,
            "defence": 10,
            "level": 1,
            "max_exp": 50,
            "exp": 0,
            "max_hp": 50,
            "hp": 42,
            "max_mp": 100,
            "mp": 1}
}
```
These data send to the client whenever the character's data change or the player login. It includes `hp`, `mp`, `exp` and other attributes.


# equipments
```
{"equipments": {"<EQUIPMENT_POS>": null,
                "<EQUIPMENT_POS>": {"dbref": "<DBREF>", "name": "<NAME>", "desc": "<DESC>"}}
}
```
These data send to the client whenever the character's equipments change or the player login. If there is no equipment on the position, the value will be set to `nil`. If there is an equipment, the value will be the equipment's `name`, `dbref` and `desc`.


# inventory
```
{"inventory": [{"name": "<OBJ_NAME>",
				"dbref": "<OBJ_DBREF>",
				"number": <OBJ_NUMBER>,
			    "desc": "<OBJ_DESC>",
			    "equipped": <IS_EQUIPPED>}]
}
```
`Inventory` contains a list of objects which are in your inventory. Each item has object's `name`, `dbref`, `number` and `desc`. If the item is an equipment, it will has an additional attribute `equipped`. This attribute shows whether the equipment is equipped.


# skills
```
{"skills": [{"name": "<SKILL_NAME>",
			 "dbref": "<SKILL_DBREF>",
			 "desc": "<SKILL_DESC>"}]}
```
`Skills` contains a list of skills that the character has. Each item has skill's `name`, `dbref`, and `desc`.


# quests
```
{"quests": [{"name": "QUEST_NAME",
			 "dbref": "QUEST_DBREF",
			 "desc": "QUEST_DESC",
			 "objectives": [{"desc": "<OBJECTIVE_DESC>"}
			 				<or> 
			 				{"target": "<OBJECTIVE_TARGET>",
							 "object": "<OBJECTIVE_OBJECT>",
			 				 "total": <TARGET_NUMBER>,
			 				 "achieved": <ACHIEVED_NUMBER>}]}]
}
```
`Quests` contains a list of quests that the character is doing. It has `name`, `dbref` and `desc`. The `objectives` is a list of quest objectives. The value can be the objective's desc or the objective's detail information.


# look_obj
```
{"look_obj": {"name": "<OBJ_NAME>",
              "desc": "<OBJ_DESC>",
              "dbref": "<OBJ_DBREF>",
              "cmds": [{"cmd": "<COMMAND_KEY>",
                        "name": "<COMMAND_NAME>",
                        "args": "<COMMAND_ARGS>"}]}
}
```
When a player send a `look` command to the server to looking at an object, the server will send back these data. These data is the object's appearance.
`name` is the name of the object that the player is looking at.
`desc` is the description of the object that the player is looking at.
`dbref` is the dbref of the object that the player is looking at.
`cmds` is a list of commands that the player can do on the object.
    `cmd` is the key of the command.
    `name` is the name of the command to display.
    `args` is the args of the command, usually is the dbref of the object.


# look_around
```
{"look_around": {"name": "<ROOM_NAME>",
                 "desc": "<ROOM_DESC>",
                 "dbref": "<ROOM_DBREF>",
                 "cmds": [<AVAILABLE_COMMANDS>],
                 "exits": [{"name": "<EXIT_NAME>", "dbref": "<EXIT_DBREF>"}],
                 "things": [{"name": "<THING_NAME>", "dbref": "<THING_DBREF>"}],
                 "npcs": [{"name": "<NPC_NAME>", "dbref": "<NPC_DBREF>"}],
                 "players": [{"name": "<PLAYER_NAME>", "dbref": "<PLAYER_DBREF>"}],
                 "offlines": [{"name": "<OFFLINE_PLAYER_NAME>", "dbref": "<OFFLINE_PLAYER_DBREF>"}]}
}
```
When a player send a `look` command to the server to looking at a room, the server will send back these data. These data is the room's appearance and all objects that in this room.
These data are similar to the `look`, but the room has more data about other objects in it.
`exits` are a list of exits.
`things` are a list of common objects in the room.
`npcs` are a list of NPCs in the room.
`players` are online players while `offlines` are offline players.
This only return available objects to players. Objects that does not match the condition will not be sent to the players.
When a player login or moves into a room, these data will be sent to the player automatically.

