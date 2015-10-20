# Database Tables

In muddery, the whole game world is build on a series of tables. When the server starts up for the first time, the server will load these data and build the world. If you have modified some tables after the server start, you, as a builder, can use `@loadworld` command to rebuild the world and use `@reload` command to refresh data.

## World Objects

World objects are unique in the world. If you add an object to these tables, this object will appear in the location you specified. If you remove an object from these tables, this object will be remove from the game world too.

### world_rooms
key | name | typeclass | desc
--- | --- | --- | ---
room_house | HOUSE | typeclasses.rooms.Room | This is a house in your game.
room_street | STREET | typeclasses.rooms.Room | This is a street in front of house.

Rooms are basic areas in the game. They build up the whole map of the game world.<br>
`key` is the unique id of the room. This must be unique in all tables.<br>
`name` is the name of the room that shows to players.<br>
`typeclass` is the typeclass of the room.<br>
`desc` is the appearance of the room when players look at it.

### world_exits
key | name | typeclass | desc | verb | location | destination
--- | --- | --- | --- | --- | --- | ---
exit_to_street | DOOR | typeclasses.exits.Exit | Go to the street. | Go out | room_house | room_street
exit_to_house | DOOR | typeclasses.exits.Exit | Enter the house. | Enter | room_street | room_house

Characters must traverse exits to move from one room to another. Exits link rooms together. Exits are oneway, so if you want to move in and move out, you need to build two exits on each side.<br>
`key` is the unique id of the exit. This must be unique in all tables.<br>
`name` is the name of the exit that shows to players.<br>
`typeclass` is the typeclass of the exit.<br>
`desc` is the appearance of the exit when players look at it.<br>
`verb` is the name of the action of traverse. This shows to players to make the action looks better. If it is empty, the system will use a default verb.<br>
`location` is the room where the exit sets. The exit opens on this side. It must be a key of world_rooms.<br>
`destination` is the room where the exit leads to. It must be a key of world_rooms.

