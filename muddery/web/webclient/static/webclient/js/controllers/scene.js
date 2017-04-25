
var controller = {

    clear_scene: function() {
        ///////////////////////
        // clear scene box
        ///////////////////////

        $("#scene_name").empty();
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
            box.data("dbref", dbref);
        }

        // add room's name
        var room_name = "";
        try {
            room_name = text2html.parseHtml(data["name"]);
        }
        catch(error) {
        }
        $("#scene_name span").html("&gt;&gt;&gt;&gt;&gt; " + room_name +  " &lt;&lt;&lt;&lt;&lt;");

        /*
        // add room's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            uimgr.divEmpty(element).appendTo(box);
        }
        catch(error) {
        }

        uimgr.divBR().appendTo(box);

        var empty = true;
        if ("cmds" in data && data["cmds"].length > 0) {
            uimgr.divRoomCmds(data["cmds"]).appendTo(box);
            empty = false;
        }
        else {
            uimgr.divRoomCmds("").appendTo(box);
        }

        // add things
        if ("things" in data && data["things"].length > 0) {
            uimgr.divRoomThings(data["things"]).appendTo(box);
            empty = false;
        }
        else {
            uimgr.divRoomThings("").appendTo(box);
        }

        // add NPCs
        if ("npcs" in data && data["npcs"].length > 0) {
            uimgr.divRoomNpcs(data["npcs"]).appendTo(box);
            empty = false;
        }
        else {
            uimgr.divRoomNpcs("").appendTo(box);
        }

        // add players
        if ("players" in data && data["players"].length > 0) {
            uimgr.divRoomPlayers(data["players"]).appendTo(box);
            empty = false;
        }
        else {
            uimgr.divRoomPlayers("").appendTo(box);
        }

        if (!empty) {
            uimgr.divBR().appendTo(box);
        }

        // add exits
        // sort exits by direction
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

        uimgr.divRoomExits(room_exits, room_name).appendTo(box);

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
};