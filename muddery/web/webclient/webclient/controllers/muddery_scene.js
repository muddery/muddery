
if (typeof(require) != "undefined") {
    require("./base_controller.js");
}

/*
 * Derive from the base class.
 */
function MudderyScene(el) {
	BaseController.call(this, el);
}

MudderyScene.prototype = prototype(BaseController.prototype);
MudderyScene.prototype.constructor = MudderyScene;

/*
 * Reset the view's language.
 */
MudderyScene.prototype.resetLanguage = function() {
	this.select("#scene_view_objects").text($$.trans("Objects: "));
	this.select("#scene_view_npcs").text($$.trans("NPCs: "));
	this.select("#scene_view_players").text($$.trans("Players: "));
}

/*
 * Bind events.
 */
MudderyScene.prototype.bindEvents = function() {
	this.onClick("#scene_commands_container", "button", this.onCommand);
	this.onClick("#scene_things_container", "a", this.onLook);
	this.onClick("#scene_npcs_container", "a", this.onLook);
	this.onClick("#scene_players_container", "a", this.onLook);
	this.onClick("#scene_exits_container", "a", this.onExit);
}

/*
 * On click a command.
 */
MudderyScene.prototype.onCommand = function(element) {
    var cmd = this.select(element).data("cmd_name");
    var args = this.select(element).data("cmd_args");
    $$.commands.doCommandLink(cmd, args);
}

/*
 * On look an object.
 */
MudderyScene.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * On go to an exit.
 */
MudderyScene.prototype.onExit = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doGoto(dbref);
}

/*
 * Clear the view.
 */
MudderyScene.prototype.clearScene = function() {
    this.select("#scene_name_content").empty();
    this.select("#scene_desc_content").empty();

    this.clearElements("#scene_commands_container");
    this.clearElements("#scene_things_container");
    this.clearElements("#scene_npcs_container");
    this.clearElements("#scene_players_container");

    for (var i = 0; i < 9; ++i) {
        this.clearElements("#scene_exits_" + i);
        this.select("#scene_link_" + i).hide();
    }
}

/*
 * Set the scene's data.
 */
MudderyScene.prototype.setScene = function(scene) {
    this.clearScene();

    // add room's dbref
    var dbref = "";
    if ("dbref" in scene) {
        dbref = scene["dbref"];
    }
    this.select("#scene_box_scene").data("dbref", dbref);

    // add room's name
    var room_name = $$.text2html.parseHtml(scene["name"]);
    this.select("#scene_name_content").html(room_name);

    // add room's desc
    var room_desc = $$.text2html.parseHtml(scene["desc"]);
    this.select("#scene_desc_content").html(room_desc);

    // add commands
    var commands = "cmds" in scene ? scene["cmds"]: null;
    this.addButtons("#scene_commands", "#scene_commands_container", commands);

    // add things
    var things = "things" in scene ? scene["things"]: null;
    this.addLinks("#scene_things", "#scene_things_container", things);

    // add NPCs
    var npcs = "npcs" in scene ? scene["npcs"]: null;
    this.addLinks("#scene_npcs", "#scene_npcs_container", npcs);

    // add players
    var players = "players" in scene ? scene["players"]: null;
    this.addLinks("#scene_players", "#scene_players_container", players);

    // add exits
    var exits = "exits" in scene ? scene["exits"]: null;
    this.setExitsMap(exits, room_name);

    // set background
    var backview = this.select("#scene_box_scene");
    if ("background" in scene && scene["background"]) {
        var url = settings.resource_url + scene["background"]["name"];
        backview.css("background", "url(" + url + ") no-repeat center center");
    }
    else {
        backview.css("background", "");
    }
}

/*
 * Add a new player to this scene.
 */
MudderyScene.prototype.addPlayer = function(player) {
    this.addLinks("#scene_players", "#scene_players_container", [player]);
}

/*
 * Remove a player from this scene.
 */
MudderyScene.prototype.removePlayer = function(player) {
    this.select("#scene_obj_" + player["dbref"].slice(1)).remove();

	if (this.select("#scene_players_container>:not(.template)").length == 0) {
	    // No other players.
		this.select("#scene_players").hide();
	}
}

/*
 * Add new objects to this scene.
 */
MudderyScene.prototype.addObjects = function(objects) {
    // add things
    var things = "things" in objects ? objects["things"]: null;
    if (things) {
        this.addLinks("#scene_things", "#scene_things_container", things);
    }

    // add NPCs
    var npcs = "npcs" in objects ? objects["npcs"]: null;
    if (npcs) {
        this.addLinks("#scene_npcs", "#scene_npcs_container", npcs);
    }

    // add players
    var players = "players" in objects ? objects["players"]: null;
    if (players) {
        this.addLinks("#scene_players", "#scene_players_container", players);
    }
}

/*
 * Remove objects from this scene.
 */
MudderyScene.prototype.removeObjects = function(objects) {
    for (var key in objects) {
        for (var i in objects[key]) {
            this.select("#scene_obj_" + objects[key][i]["dbref"].slice(1)).remove();
        }
    }

    if (this.select("#scene_things_container>:not(.template)").length == 0) {
        this.select("#scene_things").hide();
    }

    if (this.select("#scene_npcs_container>:not(.template)").length == 0) {
        this.select("#scene_npcs").hide();
    }

    if (this.select("#scene_players_container>:not(.template)").length == 0) {
        this.select("#scene_players").hide();
    }
}

/*
 * Add command button to this scene.
 */
MudderyScene.prototype.addButtons = function(block_id, container_id, data) {
    var container = this.select(container_id);
    var template = container.find("button.template");

    if (data) {
        for (var i in data) {
            var cmd = data[i];
            var name = $$.text2html.parseHtml(cmd["name"]);

            var item = this.cloneTemplate(template);
            item.data("cmd_name", cmd["cmd"])
                .data("cmd_args", cmd["args"])
                .html(name);
        }
    }

    if (block_id) {
        if (container.children().not(".template").length > 0) {
            this.select(block_id).show();
        }
        else {
            this.select(block_id).hide();
        }
    }
}

/*
 * Add object links to this scene.
 */
MudderyScene.prototype.addLinks = function(block_id, container_id, data) {
    var container = this.select(container_id);
    var template = container.find("a.template");

    if (data) {
        for (var i in data) {
            var obj = data[i];

            var name = $$.text2html.parseHtml(obj["name"]);
            if ("complete_quest" in obj && obj["complete_quest"]) {
                name += "[?]";
            }
            else if ("provide_quest" in obj && obj["provide_quest"]) {
                name += "[!]";
            }

            var item = this.cloneTemplate(template);
            item.attr("id", "obj_" + obj["dbref"].slice(1))
                .data("dbref", obj["dbref"])
                .html(name);
        }
    }

    if (block_id) {
        if (container.children().not(".template").length > 0) {
            this.select(block_id).show();
        }
        else {
            this.select(block_id).hide();
        }
    }
}

/*
 * Set a mini map of exits.
 */
MudderyScene.prototype.setExitsMap = function(exits, room_name) {
    // sort exits by direction
    var room_exits = [];
    if (exits) {
        for (var i in exits) {
            var direction = $$.map_data.getExitDirection(exits[i].key);
            // sort from north (67.5)
            if (direction < 67.5) {
                direction += 360;
            }
            room_exits.push({"data": exits[i],
                             "direction": direction
                             });
        }

        room_exits.sort(function(a, b) {return a.direction - b.direction;});
    }

    var exit_grids = [[], [], [] ,[] ,[], [], [], [], []];
    for (var i in room_exits) {
        var index = $$.map_data.getDirectionIndex(room_exits[i]["direction"]);
        exit_grids[index].push(room_exits[i]["data"]);
    }

    // reverse the upper circle elements
    for (var i = 0; i < 4; ++i) {
        exit_grids[i].reverse();
    }

    // add exits to table
    for (var i in exit_grids) {
        var grid_id = "#scene_exits_" + i;
        var link_id = "#scene_link_" + i;
        this.addExits(link_id, grid_id, exit_grids[i]);
    }

    // If the center grid is empty, show room's name in the center grid.
    if (exit_grids[4].length == 0) {
        this.addText("", "#scene_exits_4", room_name);
    }
}

/*
 * Add exits to this scene.
 */
MudderyScene.prototype.addExits = function(line_id, container_id, data) {
    var container = this.select(container_id);
    var template = container.find("a.template");

    if (data) {
        for (var i in data) {
            var obj = data[i];
            var name = $$.text2html.parseHtml(obj["name"]);

            var item = this.cloneTemplate(template);
            item.attr("id", "scene_obj_" + obj["dbref"].slice(1))
                .data("dbref", obj["dbref"])
                .html(name);
        }
    }

    if (line_id) {
        if (container.children().not(".template").length > 0) {
            this.select(line_id).show();
        }
        else {
            this.select(line_id).hide();
        }
    }
}

/*
 * Add object texts to this scene.
 */
MudderyScene.prototype.addText = function(block_id, container_id, text) {
    var container = this.select(container_id);
    var template = container.find("span.template");

    var has_text = false;
    if (text) {
        var item = this.cloneTemplate(template);
        item.html(text);
        has_text = true;
    }

    if (block_id) {
        if (has_text) {
            this.select(block_id).show();
        }
        else {
            this.select(block_id).hide();
        }
    }
}
