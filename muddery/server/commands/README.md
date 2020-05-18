# Commands

This folder holds modules for implementing one's own commands and
command sets. 

In Muddery, all commands are in format of JSON. It has two parts:
```
{"cmd":  <command's key>,
 "args": <object's dbref>
}
```

`cmd` is the unique key of a command. `args` is the command's args.

These are commands that common players can use.

### Common Commands

* look
```
{"cmd":"look",
 "args":<object's dbref>
}
```
Observe your location or objects in your vicinity.


* inventory
```
{"cmd":"inventory",
 "args":""
}
```
Show everything in your inventory.


* goto
```
{"cmd":"goto",
 "args":<exit's dbref>
}
```
Tranvese an exit, go to the destination of the exit.


* talk
```
{"cmd":"talk",
 "args":<NPC's dbref>
}
```
Talk to an NPC, show all available dialogues.


* dialogue.
```
{"cmd":"dialogue",
 "args":{"npc":<npc's dbref>,
         "dialogue":<current dialogue>,
         "sentence":<current sentence>}
}
```
This command finishes current sentence and get next sentences.
`dialogue` and `sentence` in args refer to the current sentence.


* loot
```
{"cmd":"loot",
 "args":<object's dbref>
}
```
This command pick out random objects from the loot list and give them to the character.


* use
```
{"cmd":"use",
 "args":<object's dbref>
}
```
Use the specified object.
Different objects can have different results.


* equip
```
{"cmd":"equip",
 "args":<object's dbref>
}
```
Put on an equipment and add its attributes to the character.


* take off
```
{"cmd":"takeoff",
 "args":<object's dbref>
}
```
Take off an equipment and remove its attributes from the character.


* cast skill
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
Cast a skill when the caller is not in combat. If does not have target, cast it to the caller itself.


* attack
```
{"cmd":"attack",
 "args":<object's dbref>}
}
```
This will initiate a combat with the target. If the target is already in combat, the caller will join its combat.


* unlock_exit
```
{"cmd":"unlock_exit",
 "args":<object's dbref>
}
```
A character must unlock a LockedExit before tranvese it.


### Combat Commands

* combat info
```
{"cmd":"combat_info",
 "args":""
}
```
Observes your combat, get combat informtions.


* combat skill
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
Cast a skill when the caller is in combat. If does not have target, cast it to the caller itself.


### Player Commands

* quit
```
{"cmd":"quit",
 "args":""
}
```
Gracefully disconnect your current session from the game.


### Unloggedin Commands

* connect account
```
{"cmd":"connect",
 "args":{
    "playername":<playername>,
    "password":<password>
    }
}
```
Connect to the game.


* create account
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


* create account and login
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


* look
```
{"cmd":"look",
 "args":""
}
```
Look when in unlogged-in state. It will display the connect screen.
