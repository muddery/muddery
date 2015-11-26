/*
Muddery map (javascript component)
*/

var map = {
    _map_data: {"rooms": {},
                "paths": {}},

    _current_location: null,

    _svg_width: 290,
    _svg_height: 230,
    _room_size: 40,
    _scale: 75.0,

    setData: function(data) {
        this._map_data = data;
    },

    setCurrentLocation: function(location) {
        this._current_location = location;
    },

    revealMap: function(data) {
        // add data to map

        if (data && "rooms" in data) {
            // add rooms
            for (var key in data.rooms) {
                if (!(key in this._map_data.rooms)) {
                    this._map_data.rooms[key] = data.rooms[key];
                }
            }
        }

        if (data && "paths" in data) {
            // add paths
            for (var begin in data.paths) {
                if (!(begin in this._map_data.paths)) {
                    this._map_data.paths[begin] = {};
                }

                for (var end in data.paths[begin]) {
                    this._map_data.paths[begin][end] = true;
                }
            }
        }
    },

    showMap: function() {
        var layer = $('<div>').addClass('overlayer').attr('id', 'overlayer');
        layer.prependTo($("body"));

        var box = $('<div>').attr('id', 'map_box');
        box.prependTo($("body"));

        var button = $('<div>').attr('id', 'close_button')
                               .appendTo(box)

        var input = $('<input>').addClass('close')
                                .attr('type', 'image')
                                .attr('id', 'button_close')
                                .attr('src', resource.close_button)
                                .attr('alt', 'close')
                                .attr('onclick', 'webclient.doCloseMap()')
                                .appendTo(button)

        webclient.doSetSizes();

        if (!(this._current_location &&
            this._current_location in this._map_data.rooms)){
            // does not have current location, can not show map.
            return;
        }
        var current_room = this._map_data.rooms[this._current_location];

		var svg = d3.select('#map_box')
					.append('svg')
                    .attr('id', 'map_svg')
                    .attr('width', this._svg_width)
                    .attr('height', this._svg_height);

        var scale = this._scale;
        var room_size = this._room_size;
        var origin_x = this._svg_width / 2;
        var origin_y = this._svg_height / 2;

        if (current_room[1]) {
            // set origin point
            origin_x -= current_room[1][0] * scale;
            origin_y -= current_room[1][1] * scale;
        }

        if (current_room[1] &&
            this._map_data.paths) {
            // get path positions
            var path_data = [];
            for (var begin in this._map_data.paths) {
                for (var end in this._map_data.paths[begin]) {
                    if (begin in this._map_data.rooms &&
                        this._map_data.rooms[begin][1] &&
                        end in this._map_data.rooms &&
                        this._map_data.rooms[end][1]) {
                        path_data.push([this._map_data.rooms[begin][1],    // room1 posision
                                        this._map_data.rooms[end][1]]);  // room2 posision
                    }
                }
            }

            svg.selectAll("line")
                        .data(path_data)
                        .enter()
                        .append("line")
                        .attr("x1",  function(d, i) {
                              return d[0][0] * scale + origin_x;
                              })
                        .attr("y1",  function(d, i) {
                              return d[0][1] * scale + origin_y;
                              })
                        .attr("x2",  function(d, i) {
                              return d[1][0] * scale + origin_x;
                              })
                        .attr("y2",  function(d, i) {
                              return d[1][1] * scale + origin_y;
                              })
                        .attr("stroke", "grey")
                        .attr("stroke-width", 2);
        }

        if (this._map_data.rooms) {
            // get room positions
            var room_data = [];

            if (current_room[1]) {
                for (var key in this._map_data.rooms) {
                    if (this._map_data.rooms[key][1]) {
                        room_data.push([util.truncate_string(this._map_data.rooms[key][0], 10, true),   // room's name
                                        this._map_data.rooms[key][1]]);     // room's position
                    }
                }
            }
            else {
                // does not have current position, only show current room at center.
                room_data.push([util.truncate_string(current_room[0], 10, true),   // room's name
                                [0, 0]]);     // room's position
            }

            svg.selectAll("rect")
                          .data(room_data)
                          .enter()
                          .append("rect")
                          .attr("x", function(d, i) {
                                return d[1][0] * scale - room_size / 2 + origin_x;
                                })
                          .attr("y", function(d, i) {
                                return d[1][1] * scale - room_size / 2 + origin_y;
                                })
                          .attr("width", room_size)
                          .attr("height", room_size)
                          .attr("stroke", "grey")
                          .attr("stroke-width", 2);

            svg.selectAll("text")
                          .data(room_data)
                          .enter()
                          .append("text")
                          .attr("x", function(d, i) {
                                return d[1][0] * scale + origin_x;
                                })
                          .attr("y", function(d, i) {
                                return d[1][1] * scale + origin_y;
                                })
                          .attr("dy", ".3em")
                          .attr("text-anchor", "middle")
                          .attr("font-family", "sans-serif")
                          .attr("font-size", "13px")
                          .attr("fill", "white")
                          .text(function(d) {
                                return d[0];
                                });
        }
    },
}