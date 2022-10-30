
MudderyMapData = function() {
}

MudderyMapData.prototype = {
    _map_areas: {},     // area's key: {
                        //     "name": area's name,
                        //     "icon": area's icon,
                        //     "desc": area's description,
                        //     "background": area's background,
                        // }

    _map_rooms: {},     // room's key: {"name": room's name,
                        //              "icon": room's icon,
                        //              "area": room's area,
                        //              "pos": position}

    _map_exits: {},     // exit's key: {"location": location,
                        //              "destination": destination}

    _map_paths: {},     // room's key: [room's neighbour1,
                        //              room's neighbour2,
                        //              ...]

    _current_location: null,

    _revealed_maps: {},

    queryMap: function() {
        if (Object.keys(this._map_areas).length == 0) {
            // Query map data if there is no map data.
            core.command.queryMap(function(code, data, msg) {
                if (code == 0) {
                    core.map_data.setMapData(data);
                }
                else {
                    mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
                }
            });
        }
    },

    setMapData: function(data) {
        this._map_areas = {};
        this._map_rooms = {};
        this._map_exits = {};
        this._map_paths = {};

        for (var area_key in data) {
            var area_map = data[area_key];

            this._map_areas[area_key] = area_map;
            var rooms = area_map["rooms"];

            // Add room.
            for (var room_key in rooms) {
                rooms[room_key]["area"] = area_key;
            }
            this._map_rooms = Object.assign(this._map_rooms, rooms);

            // Add exits.
            for (var room_key in rooms) {
                var exits = rooms[room_key]["exits"];
                for (var i = 0; i < exits.length; i++) {
                    var exit_key = exits[i]["key"];
                    if (!(exit_key in this._map_exits)) {
                        exits[i]["location"] = room_key;
                        this._map_exits[exit_key] = exits[i];
                    }
                }
            }

            for (var exit_key in this._map_exits) {
                var location = this._map_exits[exit_key]["location"];
                var destination = this._map_exits[exit_key]["destination"];
                if (location in this._map_paths) {
                    this._map_paths[location].push(destination);
                }
                else {
                    this._map_paths[location] = [destination];
                }
            }
        }
    },

    clearCharacterData: function() {
   	 	this._current_location = null;
   	 	this._revealed_maps = {};
    },

    setCurrentLocation: function(location) {
        this._current_location = location;
    },

    getCurrentLocation: function(location) {
        return this._current_location;
    },

    getCurrentRoomMap: function() {
        if (!this._current_location) {
            return;
        }

        if (!(this._current_location["room"] in this._map_rooms)) {
            return;
        }

        return this._map_rooms[this._current_location["room"]];
    },

    revealMaps: function(data) {
        // save revealed maps
        this._revealed_maps = data;
    },

    getExitDirection: function(exit) {
        // get the degree of the path
        // from 0 to 360
        if (!(exit in this._map_exits)) {
            return;
        }

        var location_key = this._map_exits[exit]["location"];
        if (!location_key in this._map_rooms) {
            return;
        }

        var destination_key = this._map_exits[exit]["destination"];
        if (!destination_key in this._map_rooms) {
            return;
        }

        var from_area = this._map_rooms[location_key]["area"];
        var to_area = this._map_rooms[destination_key]["area"];
        if (from_area !== to_area) {
            return;
        }

        var from = this._map_rooms[location_key]["pos"];
        var to = this._map_rooms[destination_key]["pos"];
        if (!from || !to) {
            return;
        }

        var dx = to[0] - from[0];
        var dy = to[1] - from[1];
        var degree = null;
        if (dx == 0) {
            if (dy < 0) {
                degree = 90;
            }
            else if (dy > 0) {
                degree = 270;
            }
        }
        else {
            degree = Math.atan(-dy / dx) / Math.PI * 180;

            if (dx < 0) {
                degree += 180;
            }
        }

        return degree;
    },

    getDirectionName: function(degree) {
        if (degree == null) {
            return "";
        }

        var direction = "";
        degree = degree - Math.floor(degree / 360) * 360;
        if (degree < 22.5) {
            direction = _("(E)");
        }
        else if (degree < 67.5) {
            direction = _("(NE)");
        }
        else if (degree < 112.5) {
            direction = _("(N)");
        }
        else if (degree < 157.5) {
            direction = _("(NW)");
        }
        else if (degree < 202.5) {
            direction = _("(W)");
        }
        else if (degree < 247.5) {
            direction = _("(SW)");
        }
        else if (degree < 292.5) {
            direction = _("(S)");
        }
        else if (degree < 337.5) {
            direction = _("(SE)");
        }
        else {
            direction = _("(E)");
        }

        return direction;
    },

    getDirectionIndex: function(degree) {
        // index of direction:
        // 0  1  2
        // 3  4  5
        // 6  7  8
        // default direction index is 4
        if (degree == null) {
            return 4;
        }

        var direction = 5;
        degree = degree - Math.floor(degree / 360) * 360;
        if (degree < 22.5) {
            direction = 5;
        }
        else if (degree < 67.5) {
            direction = 2;
        }
        else if (degree < 112.5) {
            direction = 1;
        }
        else if (degree < 157.5) {
            direction = 0;
        }
        else if (degree < 202.5) {
            direction = 3;
        }
        else if (degree < 247.5) {
            direction = 6;
        }
        else if (degree < 292.5) {
            direction = 7;
        }
        else if (degree < 337.5) {
            direction = 8;
        }
        else {
            direction = 5;
        }

        return direction;
    },
};
