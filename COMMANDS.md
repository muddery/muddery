# Commands

Players can send commands to the server. In Muddery, all commands are in format of JSON. It has two parts:
```
{"cmd":  <command's key>,
 "args": <command's arguments>
}
```

`cmd` is the unique key of a command. `args` is the command's arguments.

Here are main commands that normal players can use.

## Common Commands

These commands are available when a character is in common state (not in combat).

### look
```
{"cmd":"look",
 "args":<object's dbref>
}
```
Observe your location or other objects.


### inventory
```
{"cmd":"inventory",
 "args":""
}
```
Show everything in your inventory.


### goto
```
{"cmd":"goto",
 "args":<exit's dbref>
}
```
Traverse an exit, go to the destination.


### talk
```
{"cmd":"talk",
 "args":<NPC's dbref>
}
```
Talk to an NPC, show all available dialogues.


### dialogue
```
{"cmd":"dialogue",
 "args":{"npc":<npc's dbref>,
         "dialogue":<current dialogue's key>,
         "sentence":<current sentence's ordinal>}
}
```
This command finishes current sentence and get next sentences.<br>
`dialogue` and `sentence` in args are used to specify the current sentence.


### loot
```
{"cmd":"loot",
 "args":<object's dbref>
}
```
This command picks out objects from the loot list and give them to the player.


### use
```
{"cmd":"use",
 "args":<object's dbref>
}
```
Use the specified object.<br>
Different objects can have different results.


### equip
```
{"cmd":"equip",
 "args":<object's dbref>
}
```
Put on an equipment and add its attributes to the character.


### take off
```
{"cmd":"takeoff",
 "args":<object's dbref>
}
```
Take off an equipment and remove its attributes from the character.


### cast skill
```
{"cmd":"castskill",
 "args":<skill's key>}
}
```
or
```
{"cmd":"castskill",
 "args":{"skill":<skill's key>,
         "target":<skill's target>}
}
```
Cast a skill when a character is not in combat. If no target, cast it to the character itself.


### attack
```
{"cmd":"attack",
 "args":<target's dbref>}
}
```
This will initiate a combat with the target. If the target is already in combat, the caller will join its combat.


### unlock_exit
```
{"cmd":"unlock_exit",
 "args":<object's dbref>
}
```
A character must unlock a LockedExit before tranvese it.


## Combat Commands

These commands are available in combat.

### combat info
```
{"cmd":"combat_info",
 "args":""
}
```
Observes your combat, get combat informations.


### combat skill
```
{"cmd":"combat_skill",
 "args":<skill's key>}
}
```
or
```
{"cmd":"combat_skill",
 "args":{"skill":<skill's key>,
         "target":<skill's target>}
}
```
Cast a skill when a character is in combat. If no target, cast it to the character itself.


## Player Commands

These commands are used to control the player.

### quit
```
{"cmd":"quit",
 "args":""
}
```
Gracefully disconnect your character from the game.


## Unloggedin Commands

These commands are available when a player have not logged in.

### connect account
```
{"cmd":"connect",
 "args":{
    "playername":<playername>,
    "password":<password>
    }
}
```
Connect to the game.


### create account
```
{"cmd":"create_account",
 "args":{
    "playername":<playername>,
    "nickname":<nickname>,
    "password":<password>
    }
}
```
Create a new player account.


### create account and login
```
{"cmd":"create_connect",
 "args":{
    "playername":<playername>,
    "nickname":<nickname>,
    "password":<password>
    }
}
```
Create a new player account and login.


### look
```
{"cmd":"look",
 "args":""
}
```
Look when in unlogged-in state. It will display the connect screen.
