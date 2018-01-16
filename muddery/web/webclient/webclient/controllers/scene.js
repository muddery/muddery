//@ sourceURL=/controller/scene.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#view_objects").text($$("Objects: "));
	$("#view_npcs").text($$("NPCs: "));
	$("#view_players").text($$("Players: "));
}

/*
 * On click a command.
 */
Controller.prototype.onCommand = function(event) {
    var cmd = $(this).data("cmd_name");
    var args = $(this).data("cmd_args");
    $$.commands.doCommandLink(cmd, args);
}

/*
 * On look an object.
 */
Controller.prototype.onLook = function(caller) {
    var dbref = $(this).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * On go to an exit.
 */
Controller.prototype.onExit = function(caller) {
    var dbref = $(this).data("dbref");
    $$.commands.doGoto(dbref);
}

/*
 * Clear the view.
 */
Controller.prototype.clearScene = function() {
    $("#name_content").empty();
    $("#desc_content").empty();

    this.clearElements("#commands_container");
    this.clearElements("#things_container");
    this.clearElements("#npcs_container");
    this.clearElements("#players_container");

    for (var i = 0; i < 9; ++i) {
        this.clearElements("#exits_" + i);
        $("#link_" + i).hide();
    }
}

/*
 * Set the scene's data.
 */
Controller.prototype.setScene = function(scene) {
    this.clearScene();

    // add room's dbref
    var dbref = "";
    if ("dbref" in scene) {
        dbref = scene["dbref"];
    }
    $("#box_scene").data("dbref", dbref);

    // add room's name
    var room_name = $$.text2html.parseHtml(scene["name"]);
    $("#name_content").html(room_name);

    // add room's desc
    var room_desc = $$.text2html.parseHtml(scene["desc"]);
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
    var exits = "exits" in scene ? scene["exits"]: null;
    this.setExitsMap(exits, room_name);

    // set background
    var backview = $("#box_scene");
    if ("background" in scene && scene["background"]) {
        var url = $$.settings.resource_url + scene["background"]["name"];
        backview.css("background", "url(" + url + ") no-repeat center center");
    }
    else {
        backview.css("background", "");
    }
}

/*
 * Add a new player to this scene.
 */
Controller.prototype.addPlayer = function(player) {
    this.addLinks("#players", "#players_container", [player]);
}

/*
 * Remove a player from this scene.
 */
Controller.prototype.removePlayer = function(player) {
    $("#obj_" + player["dbref"].slice(1)).remove();

	if ($("#players_container>:not(.template)").length == 0) {
	    // No other players.
		$("#players").hide();
	}
}

/*
 * Add new objects to this scene.
 */
Controller.prototype.addObjects = function(objects) {
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
}

/*
 * Remove objects from this scene.
 */
Controller.prototype.removeObjects = function(objects) {
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
}

/*
 * Add command button to this scene.
 */
Controller.prototype.addButtons = function(block_id, container_id, data) {
    var container = $(container_id);
    var template = container.find("input.template");

    if (data) {
        for (var i in data) {
            var cmd = data[i];
            var name = $$.text2html.parseHtml(cmd["name"]);

            var item = this.cloneTemplate(template);
            item.removeClass("template")
                .data("cmd_name", cmd["cmd"])
                .data("cmd_args", cmd["args"])
                .html(name)
                .bind("click", this.onCommand);
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
}

/*
 * Add object links to this scene.
 */
Controller.prototype.addLinks = function(block_id, container_id, data) {
    var container = $(container_id);
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
            item.removeClass("template")
                .attr("id", "obj_" + obj["dbref"].slice(1))
                .data("dbref", obj["dbref"])
                .html(name)
                .bind("click", this.onLook);
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
}

/*
 * Set a mini map of exits.
 */
Controller.prototype.setExitsMap = function(exits, room_name) {
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
        var grid_id = "#exits_" + i;
        var link_id = "#link_" + i;
        this.addExits(link_id, grid_id, exit_grids[i]);
    }

    // If the center grid is empty, show room's name in the center grid.
    if (exit_grids[4].length == 0) {
        this.addText("", "#exits_4", room_name);
    }
}

/*
 * Add exits to this scene.
 */
Controller.prototype.addExits = function(line_id, container_id, data) {
    var container = $(container_id);
    var template = container.find("a.template");

    if (data) {
        for (var i in data) {
            var obj = data[i];
            var name = $$.text2html.parseHtml(obj["name"]);

            var item = this.cloneTemplate(template);
            item.removeClass("template")
                .attr("id", "obj_" + obj["dbref"].slice(1))
                .data("dbref", obj["dbref"])
                .html(name)
                .bind("click", this.onExit);
        }
    }

    if (line_id) {
        if (container.children().not(".template").length > 0) {
            $(line_id).show();
        }
        else {
            $(line_id).hide();
        }
    }
}

/*
 * Add object texts to this scene.
 */
Controller.prototype.addText = function(block_id, container_id, text) {
    var container = $(container_id);
    var template = container.find("span.template");

    var has_text = false;
    if (text) {
        var item = this.cloneTemplate(template);
        item.removeClass("template")
            .html(text);
        has_text = true;
    }

    if (block_id) {
        if (has_text) {
            $(block_id).show();
        }
        else {
            $(block_id).hide();
        }
    }
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
