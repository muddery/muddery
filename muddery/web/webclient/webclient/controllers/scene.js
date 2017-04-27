
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

        for (var i = 0; i < 9; ++i) {
            this.clear_items("#exits_" + i);
            $("#link_" + i).hide();
        }
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
        this.add_buttons("#commands", "#commands_content", contents);

        // add things
        contents = "things" in data ? data["things"]: null;
        this.add_links("#things", "#things_content", contents, "look");

        // add NPCs
        contents = "npcs" in data ? data["npcs"]: null;
        this.add_links("#npcs", "#npcs_content", contents, "look");

        // add players
        contents = "players" in data ? data["players"]: null;
        this.add_links("#players", "#players_content", contents, "look");

        // add exits
        // sort exits by direction
        var map = parent.map;
        var room_exits = [];
        if ("exits" in data) {
            for (var i in data["exits"]) {
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
        
        var exit_grids = [[], [], [] ,[] ,[], [], [], [], []];
        for (var i in room_exits) {
        	var index = map.getDirectionIndex(room_exits[i]["direction"]);
        	exit_grids[index].push(room_exits[i]["data"]);
        }
        
        // reverse the upper circle elements
        for (var i = 0; i < 4; ++i) {
        	exit_grids[i].reverse();
        }

        // add exits to table
        for (var i in exit_grids) {
            var grid_id = "#exits_" + i;
            var link_id = "#link_" + i;
            this.add_links(link_id, grid_id, exit_grids[i], "goto");
        }

        // If the center grid is empty, show room's name in the center grid.
        if (exit_grids[4].length == 0) {
            this.add_text("", "#exits_4", room_name);
        }

        // set background
        var backview = $("#box_scene");
        if ("background" in data && data["background"]) {
            var url = settings.resource_location + data["background"];
            backview.css("background", "url(" + url + ") no-repeat center center");
        }
        else {
            backview.css("background", "");
        }
    },
        
    clear_items: function(item_id) {
    	// remove items that are not template..
    	$(item_id).children().not(".template").remove();
    },
    
    add_buttons: function(block_id, content_id, data) {
    	var content = $(content_id);
		var item_template = content.find("input.template");

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                try {
                    var name = text2html.parseHtml(cmd["name"]);
                    item_template.clone()
                        .removeClass("template")
                        .attr("value", name)
                        .attr("cmd_name", cmd["cmd"])
                        .attr("cmd_args", cmd["args"])
                        .appendTo(content);

                    has_button = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (block_id) {
			if (has_button) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },
    
    add_links: function(block_id, content_id, data, command) {
    	var content = $(content_id);
		var item_template = content.find("a.template");

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
                        .removeClass("template")
                        .attr("cmd_name", command)
                        .attr("cmd_args", obj["dbref"])
                        .attr("dbref", obj["dbref"])
                        .html(name)
                        .appendTo(content);

                    has_link = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (block_id) {
			if (has_link) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },

    add_text: function(block_id, content_id, text) {
    	var content = $(content_id);
		var item_template = content.find("span.template");

		var has_text = false;
		if (text) {
            try {
                item_template.clone()
                    .removeClass("template")
                    .html(text)
                    .appendTo(content);

                has_text = true;
            }
            catch(error) {
                console.error(error.message);
            }
        }

		if (block_id) {
			if (has_text) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },

    doCommandLink: function(caller) {
        var cmd = $(caller).attr("cmd_name");
        var args = $(caller).attr("cmd_args");
        parent.commands.doCommandLink(cmd, args);
    },
};