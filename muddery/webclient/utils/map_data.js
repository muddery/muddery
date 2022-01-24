
MudderyMapData = function() {
}

MudderyMapData.prototype = {

    _map_rooms: {},     // room's key: {"name": room's name,
                        //              "icon": room's icon,
                        //              "area": room's area,
                        //              "pos": position}

    _map_exits: {},     // exit's key: {"from": location,
                        //              "to": destination}

    _map_paths: {},     // room's key: [room's neighbour1,
                        //              room's neighbour2,
                        //              ...]

    _current_location: null,

    clearData: function() {
        this._map_rooms = {};
        this._map_exits = {};
        this._map_paths = {};
   	 	_current_location: null;
    },

    setData: function(data) {
        // set map data
        this.clearData();
        this.revealMap(data);
    },

    setCurrentLocation: function(location) {
        this._current_location = location;
    },

    revealMap: function(data) {
        // add data to map
        for (var area in data) {
            var rooms = data[area];

            // Add room.
            for (var room_key in rooms) {
                rooms[room_key]["area"] = area;
            }
            this._map_rooms = Object.assign(this._map_rooms, rooms);

            // Add exits.
            var new_exits = {};
            for (var room_key in rooms) {
                var exits = rooms[room_key]["exits"];
                for (var exit_key in exits) {
                    this._map_exits[exit_key] = exits[exit_key];
                    new_exits[exit_key] = exits[exit_key];
                }
            }

            for (var exit_key in new_exits) {
                var location = new_exits[exit_key]["from"];
                var destination = new_exits[exit_key]["to"];
                if (location in this._map_paths) {
                    this._map_paths[location].push(destination);
                }
                else {
                    this._map_paths[location] = [destination];
                }
            }
        }
    },

    getExitDirection: function(exit) {
        // get the degree of the path
        // from 0 to 360
        if (!(exit in this._map_exits)) {
            return;
        }

        var location = this._map_exits[exit]["from"];
        if (!location in this._map_rooms) {
            return;
        }

        var destination = this._map_exits[exit]["to"];
        if (!destination in this._map_rooms) {
            return;
        }

        var from_area = this._map_rooms[location]["area"];
        var to_area = this._map_rooms[destination]["area"];
        if (from_area !== to_area) {
            return;
        }

        var from = this._map_rooms[location]["pos"];
        var to = this._map_rooms[destination]["pos"];
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
