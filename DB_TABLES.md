# Database Tables

In muddery, the whole game world is build on a series of tables. When the server starts up for the first time, the server will load these data and build the world. If you have modified some tables after the server start, you, as a builder, can use `@loadworld` command to rebuild the world and use `@reload` command to refresh data.

## World Objects

World objects are unique in the world. If you add an object to these tables, this object will appear in the location you specified. If you remove an object from these tables, this object will be remove from the game world too.

### world_rooms
key | name | typeclass | desc
room_house | HOUSE | typeclasses.rooms.Room | This is a house in your game.
room_street | STREET | typeclasses.rooms.Room | This is a street in front of house.

Rooms are basic areas in the game. They build up the whole map of the game world.<br>
`key` is the unique id of the object.
`name` is the name of the object that shows to players.
`typeclass` is the typeclass of the object.
`desc` is the appearance of the object when players look at it.

