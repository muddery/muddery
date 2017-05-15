
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var map_data = parent.map_data;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_objects").text(_("Objects: "));
		$("#view_npcs").text(_("NPCs: "));
		$("#view_players").text(_("Players: "));
	},
	
    clearScene: function() {
        ///////////////////////
        // clear scene box
        ///////////////////////

        $("#name_content").empty();
        $("#desc_content").empty();
        
        this.clearItems("#commands_container");
        this.clearItems("#things_container");
        this.clearItems("#npcs_container");
        this.clearItems("#players_container");

        for (var i = 0; i < 9; ++i) {
            this.clearItems("#exits_" + i);
            $("#link_" + i).hide();
        }
    },

    setScene: function(scene) {
        ///////////////////////
        // set scene box
        ///////////////////////

        this.clearScene();

        // add room's dbref
        var dbref = "";
        if ("dbref" in scene) {
            dbref = scene["dbref"];
        }
        $("#box_scene").data("dbref", dbref);

        // add room's name
        var room_name = text2html.parseHtml(scene["name"]);
        $("#name_content").html(room_name);

        // add room's desc
        var room_desc = text2html.parseHtml(scene["desc"]);
		$("#desc_content").html(room_desc);

        // add commands
        var commands = "cmds" in scene ? scene["cmds"]: null;
        this.addButtons("#commands", "#commands_container", commands);

        // add things
        var things = "things" in scene ? scene["things"]: null;
        this.addLinks("#things", "#things_container", things);

        // add NPCs
        var npcs = "npcs" in scene ? scene["npcs"]: null;
        this.addLinks("#npcs", "#npcs_container", npcs);

        // add players
        var players = "players" in scene ? scene["players"]: null;
        this.addLinks("#players", "#players_container", players);

        // add exits
        // sort exits by direction
        var room_exits = [];
        if ("exits" in scene) {
            for (var i in scene["exits"]) {
                var direction = map_data.getExitDirection(scene.exits[i].key);
                // sort from north (67.5)
                if (direction < 67.5) {
                    direction += 360;
                }
                room_exits.push({"data": scene.exits[i],
                                 "direction": direction
                                 });
            }

            room_exits.sort(function(a, b) {return a.direction - b.direction;});
        }
        
        var exit_grids = [[], [], [] ,[] ,[], [], [], [], []];
        for (var i in room_exits) {
        	var index = map_data.getDirectionIndex(room_exits[i]["direction"]);
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
            this.addLinks(link_id, grid_id, exit_grids[i]);
        }

        // If the center grid is empty, show room's name in the center grid.
        if (exit_grids[4].length == 0) {
            this.addText("", "#exits_4", room_name);
        }

        // set background
        var backview = $("#box_scene");
        if ("background" in scene && scene["background"]) {
            var url = settings.resource_url + scene["background"];
            backview.css("background", "url(" + url + ") no-repeat center center");
        }
        else {
            backview.css("background", "");
        }
    },

	addPlayer: function(player) {
        // add players
        this.addLinks("#players", "#players_container", [player]);
    },
    
    removePlayer: function(player) {
    	$("#obj_" + player["dbref"].slice(1)).remove();

		if ($("#players_container>:not(.template)").length == 0) {
			$("#players").hide();
		}
    },
    
    addObjects: function(objects) {
        // add things
        var things = "things" in objects ? objects["things"]: null;
        if (things) {
            this.addLinks("#things", "#things_container", things);
        }

        // add NPCs
        var npcs = "npcs" in objects ? objects["npcs"]: null;
        if (npcs) {
            this.addLinks("#npcs", "#npcs_container", npcs);
        }

        // add players
        var players = "players" in objects ? objects["players"]: null;
        if (players) {
            this.addLinks("#players", "#players_container", players);
        }
    },

    removeObjects: function(objects) {
        for (var key in objects) {
            for (var i in objects[key]) {
                $("#obj_" + objects[key][i]["dbref"].slice(1)).remove();
            }
        }

        if ($("#things_container>:not(.template)").length == 0) {
			$("#things").hide();
		}

		if ($("#npcs_container>:not(.template)").length == 0) {
			$("#npcs").hide();
		}

		if ($("#players_container>:not(.template)").length == 0) {
			$("#players").hide();
		}
    },
        
    clearItems: function(item_id) {
    	// Remove items that are not template.
    	$(item_id).children().not(".template").remove();
    },

    addButtons: function(block_id, container_id, data) {
    	var container = $(container_id);
		var item_template = container.find("input.template");

		if (data) {
            for (var i in data) {
                var cmd = data[i];

                var name = text2html.parseHtml(cmd["name"]);
                item_template.clone()
                    .removeClass("template")
                    .data("cmd_name", cmd["cmd"])
                    .data("cmd_args", cmd["args"])
                    .html(name)
                    .appendTo(container);
            }
        }

		if (block_id) {
			if (container.children().not(".template").length > 0) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },
    
    addLinks: function(block_id, container_id, data) {
    	var container = $(container_id);
		var item_template = container.find("a.template");

		if (data) {
            for (var i in data) {
                var obj = data[i];

                var name = text2html.parseHtml(obj["name"]);
                if ("complete_quest" in obj && obj["complete_quest"]) {
                    name += "[?]";
                }
                else if ("provide_quest" in obj && obj["provide_quest"]) {
                    name += "[!]";
                }

                item_template.clone()
                    .removeClass("template")
                    .attr("id", "obj_" + obj["dbref"].slice(1))
                    .data("dbref", obj["dbref"])
                    .html(name)
                    .appendTo(container);
            }
        }

		if (block_id) {
			if (container.children().not(".template").length > 0) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },

    addText: function(block_id, container_id, text) {
    	var container = $(container_id);
		var item_template = container.find("span.template");

		var has_text = false;
		if (text) {
            try {
                item_template.clone()
                    .removeClass("template")
                    .html(text)
                    .appendTo(container);

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
        var cmd = $(caller).data("cmd_name");
        var args = $(caller).data("cmd_args");
        commands.doCommandLink(cmd, args);
    },

    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.doLook(dbref);
    },

    doGoto: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.doGoto(dbref);
    },
};

$(document).ready(function() {
	controller.onReady();
});
