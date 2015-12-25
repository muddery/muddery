/*
Muddery map (javascript component)
*/

var map = {
    _map_data: {"rooms": {},
                "paths": {}},

    _current_location: null,

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
        var box = $('<div>')
            .attr('id', 'map_box')
            .attr('role', 'dialog')
            .css('display', 'block')
            .addClass('modal')
            .modal({backdrop: "static"})
            .prependTo($("#popup_container"));

        var boxDialog = $('<div>')
            .addClass('modal-dialog modal-lg')
            .addClass('vertical-center')
            .appendTo(box);

        var boxContent = $('<div>')
            .addClass('modal-content')
            .appendTo(boxDialog);

        var boxHeader = $('<div>')
            .addClass('modal-header')
            .appendTo(boxContent);

        boxHeader.append($('<button>')
            .attr('id', 'button_close')
            .attr('type', 'button')
            .attr('data-dismiss', 'modal')
            .attr('onclick', 'popupmgr.doCloseMap()')
            .addClass('close')
            .html('&times;'));

        boxHeader.append($('<h4>')
            .attr('id', 'map_name')
            .text(LS('MAP'))
            .addClass('modal-title'));

        var boxBody = $('<div>')
            .addClass('modal-body')
            .appendTo(boxContent);

        //set size
        var map_width = boxBody.width();
        var map_height = $('#middlewindow').height() * 0.8;

        boxBody.height(map_height);

        if (!(this._current_location &&
            this._current_location in this._map_data.rooms)){
            // does not have current location, can not show map.
            webclient.doSetPopupSize();
            return;
        }
        var current_room = this._map_data.rooms[this._current_location];

        //
		var svg = d3.select('#map_box .modal-body')
            .append('svg')
            .attr('id', 'map_svg')
            .attr('width', map_width)
            .attr('height', map_height);

        var scale = settings.map_scale;
        var room_size = settings.map_room_size;
        var origin_x = map_width / 2;
        var origin_y = map_height / 2;

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
            var current_room_index = -1;

            if (current_room[1]) {
                var count = 0;
                for (var key in this._map_data.rooms) {
                    if (this._map_data.rooms[key][1]) {
                        room_data.push([util.truncate_string(this._map_data.rooms[key][0], 10, true),   // room's name
                                        this._map_data.rooms[key][1]]);     // room's position
                        if (key == this._current_location) {
                            current_room_index = count;
                        }
                        count++;
                    }
                }
            }
            else {
                // does not have current position, only show current room at center.
                room_data.push([util.truncate_string(current_room[0], 10, true),   // room's name
                                [0, 0]]);     // room's position
                current_room_index = 0;
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
                .attr("stroke", function(d, i) {
                        return (i == current_room_index) ? "white" : "grey";
                      })
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
                .attr("font-size", "14px")
                .attr("fill", "white")
                .text(function(d) {
                        return d[0];
                      });
        }

        webclient.doSetPopupSize();
    },
}