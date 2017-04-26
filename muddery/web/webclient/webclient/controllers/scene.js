
var controller = {

    clear_scene: function() {
        ///////////////////////
        // clear scene box
        ///////////////////////

        $("#name_content").empty();
        $("#desc_content").empty();
        
        this.clear_items("#commands_content");
        this.clear_items("#things_content");
        this.clear_items("#npcs_content");
        this.clear_items("#players_content");
        this.clear_items("#exits_content");
    },

    set_scene: function(data) {
        ///////////////////////
        // set scene box
        ///////////////////////

        this.clear_scene();

        // add room's dbref
        var dbref = "";
        if ("dbref" in data) {
            dbref = data["dbref"];
        }
        $("#box_scene").data("dbref", dbref);

        // add room's name
        var room_name = "";
        try {
            room_name = text2html.parseHtml(data["name"]);
        }
        catch(error) {
            console.error(error.message);
        }
        $("#name_content").html("&gt;&gt;&gt;&gt;&gt; " + room_name +  " &lt;&lt;&lt;&lt;&lt;");

        // add room's desc
        var room_desc = "";
        try {
            room_desc = text2html.parseHtml(data["desc"]);
        }
        catch(error) {
            console.error(error.message);
        }
		$("#desc_content").html(room_desc);

        // add commands
        var contents = "cmds" in data ? data["cmds"]: null;
        this.add_commands("#commands", "#commands_content", contents);

        // add things
        contents = "things" in data ? data["things"]: null;
        this.add_objects("#things", "#things_content", contents);

        // add NPCs
        contents = "npcs" in data ? data["npcs"]: null;
        this.add_objects("#npcs", "#npcs_content", contents);

        // add players
        contents = "players" in data ? data["players"]: null;
        this.add_objects("#players", "#players_content", contents);

        // add exits
        // sort exits by direction
        var map = parent.map;
        var room_exits = [];
        if ("exits" in data) {
            for (var i in data.exits) {
                var direction = map.getExitDirection(data.exits[i].key);
                // sort from north (67.5)
                if (direction < 67.5) {
                    direction += 360;
                }
                room_exits.push({"data": data.exits[i],
                                 "direction": direction
                                 });
            }

            room_exits.sort(function(a, b) {return a.direction - b.direction;});
        }

        // add exits to grids
        for (var i in data_exits) {
            try {
                // get cell's index
                var index = 5;
                if (data_exits[i].direction) {
                    index = map.getDirectionIndex(data_exits[i].direction);
                }

                // create exit link
                var exit = data_exits[i].data;
                var name = text2html.parseHtml(exit.name);
                var grid = $("#exit_" + index);

                if (index >= 3) {
		            var item_template = grid.children().first();
		            var new_item = item_template.clone()
                        .attr("cmd_name", "goto")
                        .attr("cmd_args", exit["dbref"])
                        .attr("dbref", exit["dbref"])
                        .html(name)
                        .show()
                        .insertAfter(item_template);

                if (exitCell[index].length == 0) {
                    exitCell[index] = $("<span>").append(aHrefElement);
                }
                else if (index >= 3) {
                    aHrefElement.appendTo(exitCell[index]);
                }
                else {
                    aHrefElement.prependTo(exitCell[index]);
                }
            }
            catch(error) {
            }
        }

        // create cells
        var center = $("<center>").appendTo(divRoomExitsElement);

        var table = $("<table>").addClass("exit_table")
                                .appendTo(center);

        {
            var row = $("<tr>").appendTo(table);

            $("<td>").html(exitCell[0])
                     .attr("align", "right")
                     .appendTo(row);

            $("<td>").html(exitCell[1])
                     .attr("align", "center")
                     .appendTo(row);

            $("<td>").html(exitCell[2])
                     .attr("align", "left")
                     .appendTo(row);
        }

        {
            var row = $("<tr>").appendTo(table);

            if (exitCell[0].length > 0) {
                exitCell[3] = "\\";
            }
            $("<td>").html(exitCell[3])
                     .attr("align", "right")
                     .appendTo(row);

            if (exitCell[1].length > 0) {
                exitCell[4] = "|";
            }
            $("<td>").html(exitCell[4])
                     .attr("align", "center")
                    .appendTo(row);

            if (exitCell[2].length > 0) {
                exitCell[5] = "/";
            }
            $("<td>").html(exitCell[5])
                     .attr("align", "left")
                     .appendTo(row);
        }

        {
            var row = $("<tr>").appendTo(table);

            if (exitCell[6].length > 0) {
                exitCell[6].append("--");
            }
            $("<td>").html(exitCell[6])
                     .attr("align", "right")
                     .appendTo(row);

            if (exitCell[7].length == 0) {
                exitCell[7] = $("<span>").append($("<span>").html(rooom_name)
                                                            .addClass("exit_element"));
            }
            $("<td>").html(exitCell[7])
                     .attr("align", "center")
                     .appendTo(row);

            if (exitCell[8].length > 0) {
                exitCell[8].prepend("--");
            }
            $("<td>").html(exitCell[8])
                     .attr("align", "left")
                     .appendTo(row);
        }

        {
            var row = $("<tr>").appendTo(table);

            if (exitCell[12].length > 0) {
                exitCell[9] = "/";
            }
            $("<td>").html(exitCell[9])
                     .attr("align", "right")
                     .appendTo(row);

            if (exitCell[13].length > 0) {
                exitCell[10] = "|";
            }
            $("<td>").html(exitCell[10])
                     .attr("align", "center")
                    .appendTo(row);

            if (exitCell[14].length > 0) {
                exitCell[11] = "\\";
            }
            $("<td>").html(exitCell[11])
                     .attr("align", "left")
                     .appendTo(row);
        }

        {
            var row = $("<tr>").appendTo(table);

            $("<td>").html(exitCell[12])
                     .attr("align", "right")
                     .appendTo(row);

            $("<td>").html(exitCell[13])
                     .attr("align", "center")
                    .appendTo(row);

            $("<td>").html(exitCell[14])
                     .attr("align", "left")
                     .appendTo(row);
        }

        return divRoomExitsElement;

        /*
        // set background
        var backview = $("#box_scene");
        if ("background" in data && data["background"]) {
            var url = settings.resource_location + data["background"];
            backview.css("background", "url(" + url + ") no-repeat center center");
        }
        else {
            backview.css("background", "");
        }
        */
    },
        
    clear_items: function(item_id) {
    	// Hide the first item and remove others.
    	var first = $(item_id + ":first");
    	first.hide();
    	first.nextAll().remove();
    },
    
    add_commands: function(block_id, content_id, data) {
    	var content = $(content_id);
		var item_template = content.children().first();

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                try {
                    var name = text2html.parseHtml(cmd["name"]);
                    item_template.clone()
                        .attr("value", name)
                        .attr("cmd_name", cmd["cmd"])
                        .attr("cmd_args", cmd["args"])
                        .show()
                        .appendTo(content);

                    has_button = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (has_button) {
			$(block_id).show();
		}
		else {
			$(block_id).hide();
		}
    },
    
    add_objects: function(block_id, content_id, data) {
    	var content = $(content_id);
		var item_template = content.children().first();

		var has_link = false;
		if (data) {
            for (var i in data) {
                var obj = data[i];

                try {
                    var name = text2html.parseHtml(obj["name"]);
                    if ("complete_quest" in obj && obj["complete_quest"]) {
                        name += "[?]";
                    }
                    else if ("provide_quest" in obj && obj["provide_quest"]) {
                        name += "[!]";
                    }

                    item_template.clone()
                        .attr("cmd_name", "look")
                        .attr("cmd_args", obj["dbref"])
                        .attr("dbref", obj["dbref"])
                        .html(name)
                        .show()
                        .appendTo(content);

                    has_link = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (has_link) {
			$(block_id).show();
		}
		else {
			$(block_id).hide();
		}
    },
};