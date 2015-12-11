/*
Muddery webclient_uimgr (javascript component)
*/

var uimgr = {
    CONST_A_HREF_ONCLICK : "webclient.doCloseBox(); commands.doCommandLink(this); return false;",
    divEmpty : function(element, args) {
        var divEmptyElement = $("<div>");
        var element = arguments[0]?arguments[0]:"";
        var args = arguments[1]?arguments[1]:new Array();
        if(typeof(element) == 'string'){
            for(key in args){
                divEmptyElement.attr(key, args[key]);
            }
            divEmptyElement.text(element);
            return divEmptyElement;
        }
    },

    divBR : function() {
        var divElement = uimgr.divEmpty();
        var BRElement = $("<br>")
            .appendTo(divElement);
        return divElement;
    },

    aHref : function(href, onclick, name, args) {
        var aHrefElement = $("<a>")
            .attr("href", href)
            .attr("onclick", onclick)
            .text(name);
        for(key in args){
            aHrefElement.attr(key, args[key]);
        }
        return aHrefElement;
    },

    divRoomTabName : function(element) {
        var divRoomTabNameElement = uimgr.divEmpty();
        var roomTabNameElement = $("<span>").text("\>\>\>\>\> " + element +  " \<\<\<\<\<")
            .attr("class", "cyan")
            .appendTo(divRoomTabNameElement);
        return divRoomTabNameElement;
    },

    divRoomCenterTabName : function(element) {
        var divRoomTabNameElement = uimgr.divEmpty();
        var centerElement = $("<center>");
        var roomTabNameElement = $("<span>").text("\>\>\>\>\> " + element +  " \<\<\<\<\<")
            .attr("class", "cyan")
            .appendTo(centerElement);
        centerElement.appendTo(divRoomTabNameElement);
        return divRoomTabNameElement;
    },

    divRoomCommon : function(room_id, room_title) {
        var divRoomCommonElement = uimgr.divEmpty()
            .attr("id", room_id)
            .text(room_title);
        return divRoomCommonElement;
    },

    divRoomCmds : function(data_cmds) {
        var divRoomCmdsElement = uimgr.divRoomCommon("room_cmds", "Commands:");
        for (var i in data_cmds) {
            try {
                var cmd = data_cmds[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, cmd["name"],
                    {"cmd_name": cmd["cmd"], "cmd_args": cmd["args"], "style":"margin-left:10px;"});
                aHrefElement.appendTo(divRoomCmdsElement);
            }
            catch(error) {
            }
        }
        return divRoomCmdsElement;
    },

    divRoomExits : function(data_exits) {
        var empty = true;
        var divRoomExitsElement = uimgr.divRoomCommon("room_exits", LS("Exits:"));
        // add exits
        webclient.cache_room_exits = new Array();
        for (var i in data_exits) {
            try {
                var exit = data_exits[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, exit["name"],
                    {"cmd_name": "look", "cmd_args": exit["dbref"], "dbref": exit["dbref"], "style":"margin-left:10px;"});
                aHrefElement.appendTo(divRoomExitsElement);
                webclient.cache_room_exits.push(data_exits[i]);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Exits:"), {"id":"room_exits", "style":"display:none"});
        }
        return divRoomExitsElement;
    },

    divRoomThings : function(data_things) {
        var empty = true;
        var divRoomThingsElement = uimgr.divRoomCommon("room_things", LS("Objects:"));
        // add things
        for (var i in data_things) {
            try {
                var thing = data_things[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, thing["name"],
                    {"cmd_name": "look", "cmd_args": thing["dbref"], "dbref": thing["dbref"], "style":"margin-left:10px;"});
                aHrefElement.appendTo(divRoomThingsElement);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Objects:"), {"id":"room_things", "style":"display:none"});
        }
        return divRoomThingsElement;
    },

    divRoomNpcs : function(data_npcs) {
        var empty = true;
        var divRoomNpcsElement = uimgr.divRoomCommon("room_npcs", LS("NPCs:"));
        // add npcs
        for (var i in data_npcs) {
            try {
                var npc = data_npcs[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, npc["name"],
                    {"cmd_name": "look", "cmd_args": npc["dbref"], "dbref": npc["dbref"], "style":"margin-left:10px;"});
                if (npc["finish_quest"]) {
                    aHrefElement.text(aHrefElement.text() + "[?]");
                }
                else if (npc["provide_quest"]) {
                    aHrefElement.text(aHrefElement.text() + "[!]");
                }
                aHrefElement.appendTo(divRoomNpcsElement);
                empty = false;
            }
            catch(error) {
            }
        }

        if(empty) {
            return uimgr.divEmpty(LS("NPCs:"), {"id":"room_npcs", "style":"display:none"});
        }
        return divRoomNpcsElement;
    },

    divRoomPlayers : function(data_players) {
        var empty = true;
        var divRoomPlayersElement = uimgr.divRoomCommon("room_players", LS("Players:"));
        // add players
        for (var i in data_players) {
            try {
                var player = data_players[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, player["name"],
                    {"cmd_name": "look", "cmd_args": player["dbref"], "dbref": player["dbref"], "style":"margin-left:10px;"});
                aHrefElement.appendTo(divRoomPlayersElement);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Players:"), {"id":"room_players", "style":"display:none"});
        }
        return divRoomPlayersElement;
    },

    divObjectCommon : function(obj_id, obj_title) {
        var divObjectCommonElement = uimgr.divEmpty()
            .attr("id", obj_id)
            .text(obj_title);
        return divObjectCommonElement;
    },

    divObjectCmds : function(data_cmds) {
        var divObjectCmdsElement = uimgr.divObjectCommon("object_cmds", LS("Actions:"));
        // add cmds
        for (var i in data_cmds) {
            try {
                var cmd = data_cmds[i];
                var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, cmd["name"],
                    {"cmd_name": cmd["cmd"], "cmd_args": cmd["args"], "style":"margin-left:10px;"});
                aHrefElement.appendTo(divObjectCmdsElement);
            }
            catch(error) {
            }
        }
        return divObjectCmdsElement;
    },

    tableInventory : function(data) {
        var tableInventoryElement = $("<table>")
            .attr("class", "tab_inventory");
        var tableHeadElement = $("<thead>").appendTo(tableInventoryElement);
        var tableHeadTRElement = $("<tr>").appendTo(tableHeadElement)
            .append($("<th>").text(LS("NAME")))
            .append($("<th>").text(LS("NUM")))
            .append($("<th>").text(LS("DESC")));

        for (var i in data) {
            try {
                var obj = data[i];
                var tbodyElement = $("<tbody>").appendTo(tableInventoryElement);
                var trElement = $("<tr>").appendTo(tbodyElement);
                var tdElement = $("<td>").appendTo(trElement);
                var aHrefElement = $("<a>").appendTo(tdElement)
                    .attr("href", "#")
                    .attr("onclick", "commands.doCommandLink(this); return false;")
                    .attr("cmd_name", "look")
                    .attr("cmd_args", obj["dbref"])
                    .text(obj["name"]);

                tdElement = $("<td>").appendTo(trElement);
                tdElement.append(obj["number"]);
                if("equipped" in obj) {
                    if(obj["equipped"]) {
                        tdElement.append(LS(" (equipped)"));
                    }
                }
                tdElement = $("<td>").appendTo(trElement)
                    .append(obj["desc"]);
            }
            catch(error) {
            }
        }
        return tableInventoryElement;
    },

    tableSkills : function(data) {
        var tableSkillsElement = $("<table>")
            .attr("class", "tab_skills");
        var tableHeadElement = $("<thead>").appendTo(tableSkillsElement);
        var tableHeadTRElement = $("<tr>").appendTo(tableHeadElement)
            .append($("<th>").text(LS("NAME")))
            .append($("<th>").text(LS("DESC")));

        for (var i in data) {
            try {
                var obj = data[i];
                var tbodyElement = $("<tbody>").appendTo(tableSkillsElement);
                var trElement = $("<tr>").appendTo(tbodyElement);
                var tdElement = $("<td>").appendTo(trElement);
                var aHrefElement = $("<a>").appendTo(tdElement)
                    .attr("href", "#")
                    .attr("onclick", "commands.doCommandLink(this); return false;")
                    .attr("cmd_name", "look")
                    .attr("cmd_args", obj["dbref"])
                    .text(obj["name"]);

                tdElement = $("<td>").appendTo(trElement)
                    .append(obj["desc"]);
            }
            catch(error) {
            }
        }
        return tableSkillsElement;
    },

    tableQuests : function(data) {
        var tableQuestsElement = $("<table>")
            .attr("class", "tab_quests");
        var tableHeadElement = $("<thead>").appendTo(tableQuestsElement);
        var tableHeadTRElement = $("<tr>").appendTo(tableHeadElement)
            .append($("<th>").text(LS("NAME")))
            .append($("<th>").text(LS("DESC")))
            .append($("<th>").text(LS("OBJECTIVE")));


        console.log(JSON.stringify(data))

        for (var i in data) {
            try {
                var quest = data[i];
                var tbodyElement = $("<tbody>").appendTo(tableQuestsElement);
                var trElement = $("<tr>").appendTo(tbodyElement);
                var tdElement = $("<td>").appendTo(trElement);
                var aHrefElement = $("<a>").appendTo(tdElement)
                    .attr("href", "#")
                    .attr("onclick", "commands.doCommandLink(this); return false;")
                    .attr("cmd_name", "look")
                    .attr("cmd_args", quest["dbref"])
                    .text(quest["name"]);

                tdElement = $("<td>").appendTo(trElement)
                    .append(quest["desc"]);

                tdElement = $("<td>").appendTo(trElement);
                for (var o in quest["objectives"]) {
                    if (tdElement.text() != "") {
                        tdElement.append($("<br>"));
                    }

                    var obj = quest["objectives"][o];
                    if ("desc" in obj) {
                        tdElement.append(obj.desc);
                    }
                    else {
                        tdElement.append(obj.target + " " + obj.object);
                        tdElement.append(" " + obj.achieved + "/" + obj.total);
                    }
                }
            }
            catch(error) {
            }
        }
        return tableQuestsElement;
    },
}