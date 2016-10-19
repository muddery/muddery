/*
Muddery webclient_uimgr (javascript component)
*/

var uimgr = {
    CONST_A_HREF_ONCLICK : "popupmgr.doCloseBox(); commands.doCommandLink(this); return false;",
    divEmpty : function(element, args) {
        var divEmptyElement = $("<div>");
        var element = arguments[0]?arguments[0]:"";
        var args = arguments[1]?arguments[1]:new Array();
        if(typeof(element) == 'string'){
            for(key in args){
                divEmptyElement.attr(key, args[key]);
            }
            divEmptyElement.html(element);
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
            .html(name);
        for(key in args){
            aHrefElement.attr(key, args[key]);
        }
        return aHrefElement;
    },

    divRoomTabName : function(element) {
        var divRoomTabNameElement = uimgr.divEmpty();
        var roomTabNameElement = $("<span>").html("&gt;&gt;&gt;&gt;&gt; " + element +  " &lt;&lt;&lt;&lt;&lt;")
            .attr("class", "cyan")
            .appendTo(divRoomTabNameElement);
        return divRoomTabNameElement;
    },

    divRoomCenterTabName : function(element) {
        var divRoomTabNameElement = uimgr.divEmpty();
        var centerElement = $("<center>");
        var roomTabNameElement = $("<span>").html("&gt;&gt;&gt;&gt;&gt; " + element +  " &lt;&lt;&lt;&lt;&lt;")
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
        var divRoomCmdsElement = uimgr.divRoomCommon("room_cmds", LS("Commands") + LS(": "));
        for (var i in data_cmds) {
            try {
                var cmd = data_cmds[i];
                var name = text2html.parseHtml(cmd["name"]);
                var aHrefElement = uimgr.aHref("#",
                                               uimgr.CONST_A_HREF_ONCLICK,
                                               name,
                                               {"cmd_name": cmd["cmd"],
                                                "cmd_args": cmd["args"],
                                                 "style":"margin-left:10px;"
                                               });
                aHrefElement.appendTo(divRoomCmdsElement);
            }
            catch(error) {
            }
        }
        return divRoomCmdsElement;
    },

    divRoomExits : function(data_exits) {
        var empty = true;
        var divRoomExitsElement = uimgr.divRoomCommon("room_exits", LS("Exits") + LS(": "));
        // add exits
        for (var i in data_exits) {
            try {
                var element = $("<span>").addClass("room_element");

                if (data_exits[i].direction) {
                    var direction = map.getDirectionName(data_exits[i].direction);
                    if (direction) {
                        $("<span>").text(direction + " ")
                                   .appendTo(element);
                    }
                }

                var exit = data_exits[i].data;
                var name = text2html.parseHtml(exit.name);
                var aHrefElement = uimgr.aHref("#",
                                               uimgr.CONST_A_HREF_ONCLICK,
                                               name,
                                               {"cmd_name": "look",
                                                "cmd_args": exit.dbref,
                                                "dbref": exit.dbref
                                               });
                aHrefElement.appendTo(element);

                $("<span>").attr("id", "exit_cmd_" + exit.dbref.slice(1))
                           .addClass("exit_cmd")
                           .appendTo(element);

                element.appendTo(divRoomExitsElement);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Exits") + LS(": "), {"id":"room_exits", "style":"display:none"});
        }
        return divRoomExitsElement;
    },

    divRoomThings : function(data_things) {
        var empty = true;
        var divRoomThingsElement = uimgr.divRoomCommon("room_things", LS("Objects") + LS(": "));
        // add things
        for (var i in data_things) {
            try {
                var thing = data_things[i];
                var name = text2html.parseHtml(thing["name"]);
                var aHrefElement = uimgr.aHref("#",
                                               uimgr.CONST_A_HREF_ONCLICK,
                                               name,
                                               {"cmd_name": "look",
                                                "cmd_args": thing["dbref"],
                                                "dbref": thing["dbref"],
                                                "style":"margin-left:10px;"
                                               });
                aHrefElement.appendTo(divRoomThingsElement);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Objects") + LS(": "), {"id":"room_things", "style":"display:none"});
        }
        return divRoomThingsElement;
    },

    divRoomNpcs : function(data_npcs) {
        var empty = true;
        var divRoomNpcsElement = uimgr.divRoomCommon("room_npcs", LS("NPCs") + LS(": "));
        // add npcs
        for (var i in data_npcs) {
            try {
                var npc = data_npcs[i];
                var name = text2html.parseHtml(npc["name"]);
                var aHrefElement = uimgr.aHref("#",
                                               uimgr.CONST_A_HREF_ONCLICK,
                                               name,
                                               {"cmd_name": "look",
                                                "cmd_args": npc["dbref"],
                                                "dbref": npc["dbref"],
                                                "style":"margin-left:10px;"
                                               });
                if (npc["complete_quest"]) {
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
            return uimgr.divEmpty(LS("NPCs") + LS(": "), {"id":"room_npcs", "style":"display:none"});
        }
        return divRoomNpcsElement;
    },

    divRoomPlayers : function(data_players) {
        var empty = true;
        var divRoomPlayersElement = uimgr.divRoomCommon("room_players", LS("Players") + LS(": "));
        // add players
        for (var i in data_players) {
            try {
                var player = data_players[i];
                var name = text2html.parseHtml(player["name"]);
                var aHrefElement = uimgr.aHref("#",
                                               uimgr.CONST_A_HREF_ONCLICK,
                                               name,
                                               {"cmd_name": "look",
                                                "cmd_args": player["dbref"],
                                                "dbref": player["dbref"],
                                                "style":"margin-left:10px;"
                                               });
                aHrefElement.appendTo(divRoomPlayersElement);
                empty = false;
            }
            catch(error) {
            }
        }
        if(empty) {
            return uimgr.divEmpty(LS("Players") + LS(": "), {"id":"room_players", "style":"display:none"});
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
        var divObjectCmdsElement = uimgr.divObjectCommon("object_cmds", LS("Actions") + LS(": "));
        // add cmds
        for (var i in data_cmds) {
            try {
                var cmd = data_cmds[i];

                var html_button = $('<button>')
                    .attr('class', 'btn btn-default')
                    .attr('type', 'button')
                    .attr('onclick', uimgr.CONST_A_HREF_ONCLICK)
                    .text(cmd['name'])
                    .attr("cmd_name", cmd["cmd"])
                    .attr("cmd_args", cmd["args"]);
                html_button.appendTo(divObjectCmdsElement);

                //var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, cmd["name"],
                //    {"cmd_name": cmd["cmd"], "cmd_args": cmd["args"], "style":"margin-left:10px;"});
                //aHrefElement.appendTo(divObjectCmdsElement);
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

        for (var i in data) {
            try {
                var quest = data[i];
                var tbodyElement = $("<tbody>").appendTo(tableQuestsElement);
                var trElement = $("<tr>").appendTo(tbodyElement);
                var tdElement = $("<td>").appendTo(trElement);

                var name = quest["name"];
                if (quest["accomplished"]) {
                    name += LS("(Accomplished)");
                }
                var aHrefElement = $("<a>").appendTo(tdElement)
                    .attr("href", "#")
                    .attr("onclick", "commands.doCommandLink(this); return false;")
                    .attr("cmd_name", "look")
                    .attr("cmd_args", quest["dbref"])
                    .text(name);

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
                        tdElement.append(" " + obj.accomplished + "/" + obj.total);
                    }
                }
            }
            catch(error) {
            }
        }
        return tableQuestsElement;
    },

    connectBox: function() {
        var box = $('<div>')
            .attr('id', 'box_connect');

        $('<div>')
            .text(LS('Please connect to the server.'))
            .appendTo(box);

        return box;
    },

    loginBox: function() {
        var box = $('<div>')
            .attr('id', 'box_login');

        $('<div>')
            .text(LS('Please login.'))
            .appendTo(box);

        var table = $('<table>')
            .appendTo(box);

        // input username and password
        $('<tr>')
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'login_name')
                    .attr('type', 'text')
                    .attr('placeholder', LS('username'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'login_password')
                    .attr('type', 'password')
                    .attr('placeholder', LS('password'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .appendTo(table);

        // checkboxes
        $('<tr>')
            .attr('colspan', 2)
            .append($('<td>')
                .append($('<div>')
                    .text(LS('Save Password'))
                    .append($('<input>')
                        .attr('id', 'cb_save_password')
                        .attr('type', 'checkbox')
                        .attr('onclick', 'commands.doSetSavePassword()')))
                .append($('<div>')
                    .text(LS('Auto Login'))
                    .append($('<input>')
                        .attr('id', 'cb_auto_login')
                        .attr('type', 'checkbox'))))
            .appendTo(table);

        // buttons
        $('<tr>')
            .append($('<td>')
                .append($('<input>')
                    .attr('type', 'button')
                    .attr('onclick', 'commands.doLogin()')
                    .addClass('btn')
                    .addClass('btn-default')
                    .val(LS('Login'))))
            .appendTo(table);

        return box;
    },

    registerBox: function() {
        var box = $('<div>')
        .attr('id', 'box_register');

        var table = $('<table>')
            .appendTo(box);

        // input names
        $('<tr>')
            .append($('<td>')
                .text(LS('Name')))
            .appendTo(table);

        $('<tr>')
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'reg_name')
                    .attr('type', 'text')
                    .attr('placeholder', LS('username'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'reg_nickname')
                    .attr('type', 'text')
                    .attr('placeholder', LS('nickname'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .appendTo(table);

        // input passwords
        $('<tr>')
            .append($('<td>')
                .text(LS('Password')))
                .appendTo(table);

        $('<tr>')
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'reg_password')
                    .attr('type', 'password')
                    .attr('placeholder', LS('password'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .append($('<td>')
                .append($('<input>')
                    .attr('id', 'reg_password_again')
                    .attr('type', 'password')
                    .attr('placeholder', LS('password again'))
                    .attr('aria-describedby', 'basic-addon2')
                    .attr('autocomplete', 'off')
                    .addClass('form-control')
                    .addClass('editbox')
                    .val('')))
            .appendTo(table);

        // buttons
        $('<tr>')
            .append($('<td>')
                .append($('<br>')))
            .appendTo(table);

        $('<tr>')
            .append($('<td>')
                .append($('<input>')
                    .attr('type', 'button')
                    .attr('onclick', 'commands.doRegister()')
                    .addClass('btn')
                    .addClass('btn-default')
                    .val(LS('Register'))))
            .appendTo(table);

        return box;
    },

    sceneBox: function() {
        var box = $('<div>')
            .attr('id', 'box_scene');

        return box;
    },

    statusBox: function() {
        var box = $('<div>')
            .attr('id', 'box_status');

        return box;
    },

    equipmentBox: function() {
        var box = $('<div>')
            .attr('id', 'box_equipment');

        return box;
    },

    inventoryBox: function() {
        var box = $('<div>')
            .attr('id', 'box_inventory');

        return box;
    },

    skillBox: function() {
        var box = $('<div>')
            .attr('id', 'box_skill');

        return box;
    },

    questBox: function() {
        var box = $('<div>')
            .attr('id', 'box_quest');

        return box;
    },

    commandBox: function() {
        var box = $('<div>')
            .attr('id', 'box_command');

        $('<div>')
            .text(LS('Please input command.'))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'text')
                .attr('aria-describedby', 'basic-addon2')
                .attr('autocomplete', 'off')
                .addClass('form-control')
                .addClass('editbox')
                .val(''))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'button')
                .attr('autocomplete', 'off')
                .attr('onclick', 'commands.doSendCommand()')
                .addClass('btn')
                .addClass('button_left')
                .val(LS('SEND')))
            .appendTo(box);

        return box;
    },
}