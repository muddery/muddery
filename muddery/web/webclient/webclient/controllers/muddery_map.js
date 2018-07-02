
if (typeof(require) != "undefined") {
    require("../css/map.css");

    require("../controllers/base_controller.js");
}

/*
 * Derive from the base class.
 */
MudderyMap = function(el) {
	BasePopupController.call(this, el);
	
    // the scale of the map
    this.scale = 75;

    // the size of a room
    this.room_size = 40;

    // show room box if it does not have an icon
    this.show_room_box = false;
}

MudderyMap.prototype = prototype(BasePopupController.prototype);
MudderyMap.prototype.constructor = MudderyMap;

/*
 * Bind events.
 */
MudderyMap.prototype.bindEvents = function() {
    this.onClick("#map_close_box", this.onClose);
}

/*
 * Set element's size.
 */
MudderyMap.prototype.resetSize = function() {
	//set size
	var width = this.el.parent().width();
	var height = $('#middlewindow').height() * 0.8;

	this.el.innerWidth(width)
		   .innerHeight(height);

	// model dialogue
	var win_h = $(window).innerHeight();
	var dlg = $(".modal-dialog:visible:first");
	if (dlg.length > 0) {
		dlg.css("top", (win_h - dlg.height()) / 2);
	}
}

/*
 * Event when clicks the close button.
 */
MudderyMap.prototype.onClose = function(element) {
	$$.main.doClosePopupBox();
}
    
/*
 * Set map's configurations.
 */
MudderyMap.prototype.setMap = function(scale, room_size, show_room_box) {
    this.scale = scale;
    this.room_size = room_size;
    this.show_room_box = show_room_box;
}

/*
 * Clear the map.
 */
MudderyMap.prototype.clear = function() {
    $("#map_name").html($$.trans("MAP"));
    $("#map_svg").empty();
}
    
/*
 * Show current location's map.
 */
MudderyMap.prototype.showMap = function(location) {
	this.clear();

	if (!(location && location.key in $$.map_data._map_rooms)){
		// does not have current location, can not show map.
		return;
	}
	
	if (location["area"]) {
		var area_name = $$.text2html.parseHtml(location["area"]["name"]);
		if (area_name) {
			$("#map_name").html(area_name);
		}
	}
	
	var current_room = $$.map_data._map_rooms[location.key];

	var w_width = $(this.el).width();
	var w_height = $(this.el).height();

	var map_width = w_width;
	var map_height = w_height - $("div.modal-header").outerHeight();
	var scale = this.scale;
	var room_size = this.room_size;
	var origin_x = map_width / 2;
	var origin_y = map_height / 2;
	var current_area_key = "";		// Only show rooms and exits in the same area.
	
	if (current_room["pos"]) {
		// set origin point
		origin_x -= current_room["pos"][0] * scale;
		origin_y -= -current_room["pos"][1] * scale;

		current_area_key = current_room["area"];
	}

	//
	var svg = d3.select("#map_svg");
	svg.attr("width", map_width)
	   .attr("height", map_height);
	
	// background
	if (location["area"] && location["area"]["background"]) {
		 var x = 0;
		 var y = 0;
		 
		 if (location["area"]["background_point"]) {
			x -= location["area"]["background_point"][0];
			y -= location["area"]["background_point"][1];
		 }
		 
		 if (location["area"]["corresp_map_pos"]) {
			x += location["area"]["corresp_map_pos"][0] * scale + origin_x;
			y += -location["area"]["corresp_map_pos"][1] * scale + origin_y;
		 }

		 svg.append("image")
			.attr("x", x)
			.attr("y", y)
			.attr("width", location["area"]["background"]["width"] + "px")
			.attr("height", location["area"]["background"]["height"] + "px")
			.attr("xlink:href", settings.resource_url + location["area"]["background"]["resource"]);
	}

	if (current_room["pos"] &&
		$$.map_data._map_paths) {
		// get path positions
		var path_data = [];
		for (var begin in $$.map_data._map_paths) {
			if (begin in $$.map_data._map_rooms) {
				var from_room = $$.map_data._map_rooms[begin];

				var from_area_key = from_room["area"];
				if (from_area_key != current_area_key) {
					continue;
				}

				var from = from_room["pos"];
				for (var end in $$.map_data._map_paths[begin]) {
					if ($$.map_data._map_paths[begin][end] in $$.map_data._map_rooms) {
						var to_room = $$.map_data._map_rooms[$$.map_data._map_paths[begin][end]];

						var to_area_key = to_room["area"];
						if (to_area_key != current_area_key) {
							continue;
						}

						var to = to_room["pos"];
						if (from && to) {
							path_data.push({"from": from, "to": to});  // path posision
						}
					}
				}
			}
		}

		svg.selectAll()
			.data(path_data)
			.enter()
			.append("line")
			.attr("x1",  function(d, i) {
					return d["from"][0] * scale + origin_x;
					})
			.attr("y1",  function(d, i) {
					return -d["from"][1] * scale + origin_y;
					})
			.attr("x2",  function(d, i) {
					return d["to"][0] * scale + origin_x;
					})
			.attr("y2",  function(d, i) {
					return -d["to"][1] * scale + origin_y;
					})
			.attr("stroke", "grey")
			.attr("stroke-width", 2);
	}

	if ($$.map_data._map_rooms) {
		// get room positions
		var room_data = [];
		var current_room_index = -1;

		if (current_room["pos"]) {
			var count = 0;
			for (var key in $$.map_data._map_rooms) {
				var room = $$.map_data._map_rooms[key];
				if (room["pos"]) {
				
					var area_key = room["area"];
					if (area_key != current_area_key) {
						continue;
					}
						
					room_data.push({"name": $$.utils.truncate_string(room["name"], 10, true),
									"icon": room["icon"]? settings.resource_url + room["icon"]: null,
									"area": room["area"],
									"pos": room["pos"]});
					if (key == location.key) {
						current_room_index = count;
					}
					count++;
				}
			}
		}
		else {
			// does not have current position, only show current room at center.
			room_data.push({"name": $$.utils.truncate_string(current_room["name"], 10, true),
							"icon": current_room["icon"],
							"area": current_room["area"],
							"pos": [0, 0]});
			current_room_index = 0;
		}
		
		svg.selectAll()
			.data(room_data.filter(function(d) {
					// Draw icons.
					return d["icon"];
				  }))
			.enter()
			.append("image")
			.attr("x", function(d) {
					return d["pos"][0] * scale - room_size / 2 + origin_x;
				  })
			.attr("y", function(d) {
					return -d["pos"][1] * scale - room_size / 2 + origin_y;
				  })
			.attr("width", room_size)
			.attr("height", room_size)
			.attr("xlink:href", function(d) {
					return d["icon"];
				  });

		if (this.show_room_box) {
            svg.selectAll()
                .data(room_data.filter(function(d) {
                        // Draw rect to rooms without icon.
                        return !d["icon"];
                      }))
                .enter()
                .append("rect")
                .attr("x", function(d) {
                        return d["pos"][0] * scale - room_size / 2 + origin_x;
                      })
                .attr("y", function(d) {
                        return -d["pos"][1] * scale - room_size / 2 + origin_y;
                      })
                .attr("width", room_size)
                .attr("height", room_size)
                .attr("stroke", "grey")
                .attr("stroke-width", 1);
		}

		svg.selectAll()
			.data(room_data)
			.enter()
			.append("text")
			.attr("x", function(d) {
					return d["pos"][0] * scale + origin_x;
				  })
			.attr("y", function(d) {
					// Under the room's icon.
					return -d["pos"][1] * scale + origin_y;
				  })
			.attr("dy", function(d) {
					return d["icon"] ? room_size / 2 + 16 : 8;
				  })
			.attr("text-anchor", "middle")
			.attr("font-family", "sans-serif")
			.attr("font-size", function(d, i) {
					return (i == current_room_index) ? "14px" : "12px";
				  })
			.attr("fill", function(d, i) {
					return (i == current_room_index) ? "white" : "#eee";
				  })
			.style("text-shadow", ".1em .1em .5em #000000")
			.text(function(d) {
					return $$.text2html.clearTags(d["name"]);
				  });
	}
}
