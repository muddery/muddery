/*
Muddery webclient (javascript component)
*/

var webclient = {
    cache_room_exits : null,
    doShow : function(type, msg) {
        var data = null;
        
        if (type == "out") {
            try {
                var decode = JSON.parse(msg);
                var type = Object.prototype.toString.call(decode);
                
                if (type == "[object Object]") {
                    // Json object.
                    data = decode;
                }
                else if (type == "[object String]") {
                    // String
                    data = {"msg": decode};
                }
                else {
                    // Other types, treat them as normal text messages.
                    data = {"msg": msg};
                }
            }
            catch(err) {
                // Not JSON packed, treat it as a normal text message.
                data = {"msg": msg};
            }
        }
        else if (type == "err") {
            data = {"err": msg};
        }
        else if (type == "sys") {
            data = {"sys": msg};
        }
        else if (type == "prompt") {
            data = {"prompt": msg};
        }
        else if (type == "debug") {
            data = {"debug": msg};
        }
        else {
            data = {"msg": msg};
        }
                    
        this.displayData(data);
    },

    // display all kinds of data
    displayData : function(data) {
        for (var key in data) {
            try {
                if (key == "msg") {
                    this.displayMsg(data[key]);
                }
                else if (key == "alert") {
                    this.displayAlert(data[key]);
                }
                else if (key == "out") {
                    this.displayOut(data[key]);
                }
                else if (key == "err") {
                    this.displayErr(data[key]);
                }
                else if (key == "sys") {
                    this.displaySystem(data[key]);
                }
                else if (key == "debug") {
                    this.displayDebug(data[key]);
                }
                else if (key == "prompt") {
                    this.displayPrompt(data[key]);
                }
                else if (key == "look_around") {
                    this.displayLookAround(data[key]);
                }
                else if (key == "obj_moved_in") {
                    this.displayObjMovedIn(data[key]);
                }
                else if (key == "obj_moved_out") {
                    this.displayObjMovedOut(data[key]);
                }
                else if (key == "player_online") {
                    this.displayPlayerOnline(data[key]);
                }
                else if (key == "player_offline") {
                    this.displayPlayerOffline(data[key]);
                }
                else if (key == "look_obj") {
                    this.displayLookObj(data[key]);
                }
                else if (key == "dialogue") {
                    this.displayDialogue(data[key]);
                }
                else if (key == "status") {
                    this.displayStatus(data[key]);
                }
                else if (key == "equipments") {
                    this.displayEquipments(data[key]);
                }
                else if (key == "inventory") {
                    this.displayInventory(data[key]);
                }
                else if (key == "skills") {
                    this.displaySkills(data[key]);
                }
                else if (key == "quests") {
                    this.displayQuests(data[key]);
                }
                else if (key == "get_object") {
                    this.displayGetObject(data[key]);
                }
                else if (key == "joined_combat") {
                    combat.createCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    combat.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                    combat.displayCombatInfo(data[key]);
                }
                else if (key == "combat_commands") {
                    combat.displayCombatCommands(data[key]);
                }
                else if (key == "combat_process") {
                    combat.displayCombatProcess(data[key]);
                }
                else if (key == "combat_skill_cd") {
                    combat.displaySkillCD(data[key]);
                }
                else if (key == "current_location") {
                    map.setCurrentLocation(data[key]);
                }
                else if (key == "reveal_map") {
                    map.revealMap(data[key]);
                }
                else if (key == "revealed_map") {
                    map.setData(data[key]);
                }
                else if (key == "login") {
                    this.onLogin(data[key]);
                }
                else if (key == "logout") {
                    this.onLogout(data[key]);
                }
                else if (key == "puppet") {
                    this.onPuppet(data[key]);
                }
                else {
                    this.displayMsg(data[key]);
                }
            }
            catch(error) {
                this.displayErr("Data error.");
                console.error(error);
            }
        }
    },

    displayMsg : function(data) {
        this.displayTextMsg("msg", text2html.parseHtml(data));
    },
        
    displayAlert : function(data) {
        try {
            var msg = "";
            var button = LS("OK");
            
            var type = Object.prototype.toString.call(data);
            if (type == "[object String]") {
                msg = data;
            }
            else {
                if ("msg" in data) {
                    msg = data["msg"];
                }
                
                if ("button" in data) {
                    button = data["button"];
                }
            }

            this.showAlert(msg, button);
        }
        catch(error) {
            this.displayErr("Data error.");
            console.error(error);
        }
    },

    displayOut : function(data) {
        this.displayTextMsg("out", data);
    },

    displayErr : function(data) {
        this.displayTextMsg("err", data);
    },

    displaySystem : function(data) {
        this.displayTextMsg("sys", data);
    },

    displayDebug : function(data) {
        this.displayTextMsg("debug", data);
    },

    displayPrompt : function(data) {
        this.displayTextMsg("prompt", data);
    },

    displayTextMsg : function(type, msg) {
        var msg_wnd = $("#msg_wnd");
        if (msg_wnd.length > 0) {
            msg_wnd.stop(true);
            msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
        }

        uimgr.divEmpty("", {"class":"msg " + type})
            .append(msg)
            .appendTo(msg_wnd);

        // remove old messages
        var divs = msg_wnd.children("div");
        var max = 40;
        var size = divs.size();
        if (size > max) {
            divs.slice(0, size - max).remove();
        }
        
        // scroll message window to bottom
        // $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
        msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
    },

    displayLookAround : function(data) {
        var tab = $("#tab_room a");
        var page = $("#page_room");

        ///////////////////////
        // set room tab
        ///////////////////////
        
        // set tab's name to room's name
        var tab_name = "";
        if ("name" in data) {
            tab_name = data["name"];
        }

        if (tab_name.length == 0) {
            tab_name = "Room";
        }
        else {
            tab_name = util.truncate_string(tab_name, 10, true);
        }
        tab.text(tab_name);

        ///////////////////////
        // set room page
        ///////////////////////
        
        var content = "";
        var element = "";
        
        // add room's dbref
        var dbref = "";
        if ("dbref" in data) {
            dbref = data["dbref"];
            page.data("dbref", dbref);
        }
        
        // add room's name
        try {
            element = data["name"];
        }
        catch(error) {
            element = tab_name;
        }
        page.html("");
        uimgr.divRoomTabName(element).appendTo(page);

        // add room's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            uimgr.divEmpty(element).appendTo(page);
        }
        catch(error) {
        }

        uimgr.divBR().appendTo(page);

        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                uimgr.divRoomCmds(data["cmds"]).appendTo(page);
            }
        }

        var empty = true;
        if ("exits" in data) {
            if (data["exits"].length > 0) {
                uimgr.divRoomExits(data["exits"]).appendTo(page);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomExits("").appendTo(page);
        }

        empty = true;
        if ("things" in data) {
            if (data["things"].length > 0) {
                uimgr.divRoomThings(data["things"]).appendTo(page);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomThings("").appendTo(page);
        }

        empty = true;
        if ("npcs" in data) {
            if (data["npcs"].length > 0) {
                uimgr.divRoomNpcs(data["npcs"]).appendTo(page);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomNpcs("").appendTo(page);
        }

        empty = true;
        if ("players" in data) {
            if (data["players"].length > 0) {
                uimgr.divRoomPlayers(data["players"]).appendTo(page);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomPlayers("").appendTo(page);
        }

        this.doSetSizes();
    },
    
    displayObjMovedIn : function(data) {
        for (var key in data) {
            var page = $("#room_" + key);
            page.css("display", "");

            for (var i in data[key]) {
                try {
                    var obj = data[key][i];
                    var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, obj["name"],
                        {"cmd_name": "look", "cmd_args": obj["dbref"], "dbref": obj["dbref"], "style":"margin-left:10px;"});
                    page.append(aHrefElement);
                }
                catch(error) {
                }
            }
        }
    },

    displayObjMovedOut : function(data) {
        for (var key in data) {
            var page = $("#room_" + key);
            for (var i in data[key]) {
                try {
                    var obj = data[key][i];
                    page.find("a[dbref=" + obj["dbref"] + "]").remove();
                }
                catch(error) {
                }
            }
            
            if (page.find("a").length == 0) {
                page.css("display", "none");
            }
        }
    },
    
    displayPlayerOnline : function(data) {
        var page = $("#room_players");
        page.css("display", "");

        try {
            var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, data["name"],
                {"cmd_name": "look", "cmd_args": data["dbref"], "dbref": data["dbref"], "style":"margin-left:10px;"});
            page.append(aHrefElement);
        }
        catch(error) {
        }
    },
    
    displayPlayerOffline : function(data) {
        var page = $("#room_players");
        try {
            page.find("a[dbref=" + data["dbref"] + "]").remove();
        }
        catch(error) {
        }
        
        if (page.find("a").length == 0) {
            page.css("display", "none");
        }
    },

    displayLookObj : function(data) {

        //if cmds contains goto, display all actions of current exit
        var is_goto = false;
        var is_exit = false;

        if ("cmds" in data) {
            for (var i in data["cmds"]) {
                var cmd = data["cmds"][i];
                if(cmd["cmd"] == "goto"){
                    is_goto = true;
                }
            }
        }

        if(is_goto){
            var page = $("#room_exits");
            page.html(LS("Exits:"));
            if (webclient.cache_room_exits) {
                if (webclient.cache_room_exits.length > 0) {
                    // add exits
                    for (var i in webclient.cache_room_exits) {
                        try {
                            var exit = webclient.cache_room_exits[i];
                            var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, exit["name"],
                                {"cmd_name": "look", "cmd_args": exit["dbref"], "dbref": exit["dbref"], "style":"margin-left:10px;"});
                            aHrefElement.appendTo(page);

                            if(exit["dbref"] == data["dbref"]){
                                page.append('[');
                                is_exit = true;
                                for (var i in data["cmds"]) {
                                    try {
                                        var cmd = data["cmds"][i];
                                        var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, cmd["name"],
                                            {"cmd_name": cmd["cmd"], "cmd_args": cmd["args"], "style":"margin-left:10px;"});
                                        aHrefElement.appendTo(page);
                                    }
                                    catch(error) {
                                    }
                                }
                                page.append(']');
                            }
                        }
                        catch(error) {
                        }
                    }
                }
            }
            if(is_exit && is_goto){
                return;
            }
        }

        this.doCloseBox();
        this.createMessageBox();
        
        var page = $('#input_prompt');

        var title = $('<div>').addClass('clearfix')
                              .appendTo(page);

        var button = $('<div>').attr('id', 'close_button')
                               .appendTo(title)

        var input = $('<input>').addClass('close')
                                .attr('type', 'image')
                                .attr('id', 'button_close')
                                .attr('src', resource.close_button)
                                .attr('alt', 'close')
                                .attr('onclick', 'webclient.doCloseBox()')
                                .appendTo(button)

        // object's info
        var element = "";

        // add object's dbref
        var dbref = "";
        if ("dbref" in data) {
            dbref = data["dbref"];
            page.data("dbref", dbref);
        }
        
        // add object's name
        try {
            element = data["name"];
        }
        catch(error) {
            element = tab_name;
        }

        var name = uimgr.divRoomCenterTabName(element);
        title.append(name);

        // add object's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            uimgr.divEmpty(element).appendTo(page);
        }
        catch(error) {
        }

        uimgr.divBR().appendTo(page);

        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                uimgr.divObjectCmds(data["cmds"]).appendTo(page);
            }
        }

        // button
        /*
        var html_button = '<div><br></div>\
                             <div>\
                                <center>\
                                    <input type="button" id="button_center" value="OK" class="btn btn-primary" onClick="webclient.doCloseBox()"/>\
                                </center>\
                            </div>'
        $('#input_additional').html(html_button);
        */
        this.doSetSizes();
    },
    
    displayInventory : function(data) {
        // display player's inventory
        var page = $("#page_inventory").html("");
        uimgr.tableInventory(data).appendTo(page);
    },

    displaySkills : function(data) {
        // display player's skills
        var page = $("#page_skills").html("");
        uimgr.tableSkills(data).appendTo(page);
    },

    displayQuests : function(data) {
        // display player's quests
        var page = $("#page_quests").html("");
        uimgr.tableQuests(data).appendTo(page);
    },

    displayGetObject : function(data) {
        // show accepted objects
        try {
            var first = true;
            var accepted = data["accepted"]
            for (var key in accepted) {
                if (first) {
                    this.displayMsg(LS("You got:"));
                    first = false;
                }

                this.displayMsg(key + ": " + accepted[key]);
            }
        }
        catch(error) {
        }

        // show rejected objects
        try {
            var first = true;
            var rejected = data["rejected"];
            for (var key in rejected) {
                if (first) {
                    this.displayMsg(LS("You can not get:"));
                    first = false;
                }

                this.displayMsg(key + ": " + rejected[key]);
            }
        }
        catch(error) {
        }

        var combat_box = $('#combat_box');
        if (combat_box.length == 0) {
            // If not in combat.
            var popup_box = $('#popup_box');
            if (popup_box.length == 0) {
                // If there is no other boxes, show getting object box.
                this.displayGetObjectBox(data);
            }
        }
        else {
            // If in combat, show objects in the combat box.
            combat.displayGetObject(data);
        }
    },

    displayGetObjectBox : function(data) {
        this.doCloseBox();
        this.createMessageBox();
        
        var page = $("#input_prompt");

        // object's info
        var content = "";
        var element = "";
        var count = 0;

        // add object's name
        try {
            var first = true;
            var accepted = data["accepted"]
            for (var key in accepted) {
                element = key + ": " + accepted[key] + "<br>";
                
                if (first) {
                    content += LS("You got:") + "<br>";
                    first = false;
                }
                content += element;
                count += 1;
            }
        }
        catch(error) {
        }

        try {
            var first = true;
            var rejected = data["rejected"];
            for (var key in rejected) {
                element = key + ": " + rejected[key] + "<br>";
                
                if (first) {
                    if (count > 0) {
                        content += "<br>"
                    }
                    first = false;
                }
                content += element;
                count += 1;
            }
        }
        catch(error) {
        }
        
        if (count == 0) {
            content = LS("You got nothing.");
        }

        page.html(content);
        
        // button
        var br = $("<div>").append($("<br>"));
        $('#input_additional').append(br);

        var div = $("<div>");
		var center = $("<center>").appendTo(div);
        var html_button = $("<input>").addClass("btn btn-primary")
        							  .attr("type", "button")
        							  .attr("id", "button_center")
        							  .attr("onClick", "webclient.doCloseBox()")
        							  .val(LS("OK"))
        							  .appendTo(center);
        $('#input_additional').append(div);
        this.doSetSizes();
    },

    displayStatus : function(data) {
        // refresh prompt bar
        var bar = $("#prompt_bar");
        var prompt = "";
        var element = "";
        
        try {
            element = "<span class='white'> " + LS("HP: ");
            element += data["hp"].toString();
            element += "</span>";
            prompt += element;
        }
        catch(error) {
        }
        bar.html(prompt);
        
        // display player's status
        var block = $("#block_status");
        var content = "";
        
        // add player's status
        content += "<div>";

        try {
            element = "<div><span class='white'> " + LS("HP: ");
            element += data["hp"].toString() + "/" + data["max_hp"].toString();
            element += "</span><br></div>";
            content += element;
        }
        catch(error) {
        }

        try {
            element = "<div><span class='white'> " + LS("ATTACK: ");
            element += data["attack"].toString();
            element += "</span><br></div>";
            content += element;
        }
        catch(error) {
        }
        
        try {
            element = "<div><span class='white'> " + LS("DEFENCE: ");
            element += data["defence"].toString();
            element += "</span><br></div>";
            content += element;
        }
        catch(error) {
        }
    
        content += "</div>";
        block.html(content);
    },
        
    displayEquipments : function(data) {
        // display player's equipments
        var block = $("#block_equipments");
        var content = "";

        try {
            element = "<div>" + LS("Equipments: ");
            for (position in data) {
                element += "<br>";
                element += "&nbsp;&nbsp;" + position + LS(": ");
                if (data[position] != null) {
                    element += " <a href='#' onclick='commands.doCommandLink(this); return false;'"
                    element += " cmd_name='look'";
                    element += " cmd_args='" + data[position].dbref + "'>";
                    element += data[position].name;
                    element += "</a>"
                }
            }
            element += "</div>";
            content += element;
        }
        catch(error) {
        }
        
        content += "</div>";
        block.html(content);
    },

    displayDialogue : function(data) {
        this.showDialogue(data);
    },

    onLogin : function(data) {
        // show login UI
        $("#msg_wnd").empty();
        this.showLoginTabs();
        this.showPage("room");
        this.doSetSizes();
    },
    
    onLogout : function(data) {
        // show unlogin UI
        $("#msg_wnd").empty();
        $("#prompt_bar").empty();
        this.showUnloginTabs();
        this.showPage("login");
        this.doSetSizes();
        
        //reconnect, show the connection screen
        webclient_init();
    },
    
    onPuppet : function(data) {
        combat.setSelf(data);
    },

    doSetSizes : function() {
        // Sets the size of the message window
        var win_h = $(window).innerHeight();
        var win_w = $(window).innerWidth();

        // popup box
        var close_h = $('#close_button').outerHeight(true);
        var prom_h = $('#input_prompt').outerHeight(true);
        var add_h = $('#input_additional').outerHeight(true);
        $('#popup_box').height(close_h + prom_h + add_h);
        
        var inp_h = $('#popup_box').outerHeight(true);
        var inp_w = $('#popup_box').outerWidth(true);
        //$("#wrapper").css({'height': win_h - inp_h - 1});
        $('#popup_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

        var close_h = $('#close_button').outerHeight(true);
        var prom_h = $('#input_prompt').outerHeight(true);
        var add_h = $('#input_additional').outerHeight(true);
        $('#dialogue_box').height(close_h + prom_h + add_h);

        var inp_h = $('#dialogue_box').outerHeight(true);
        var inp_w = $('#dialogue_box').outerWidth(true);
        //$("#wrapper").css({'height': win_h - inp_h - 1});
        $('#dialogue_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

        // combat box
        var inp_h = $('#combat_box').outerHeight(true);
        var inp_w = $('#combat_box').outerWidth(true);
        $('#combat_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

        // map box
        var inp_h = $('#map_box').outerHeight(true);
        var inp_w = $('#map_box').outerWidth(true);
        $('#map_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

        if (win_h > 480) {
            var head_h = $('#site-title').outerHeight(true);
            $('#header_bar').show();
            $('#wrapper').height(win_h - head_h - 6);
        }
        else {
            $('#header_bar').hide();
            $('#wrapper').height(win_h - 6);
        }
        
        var middle_h = $('#middlewindow').outerHeight(true);
        var bottom_bar_h = 18;
        var total_h = middle_h - bottom_bar_h;
        var prompt_h = 18;
        var tab_bar_h = $('#tab_pills').outerHeight(true) - 1;
        if (tab_bar_h < 30) {
            tab_bar_h = 30;
        }
        var tab_content_max_h = 360;
        if (total_h + prompt_h + tab_bar_h > tab_content_max_h * 2) {
            $('#msg_wnd').height(middle_h - tab_bar_h - tab_content_max_h - 2);
            $('#prompt').height(prompt_h);
            $('#tab_bar').height(tab_bar_h);
            $('#tab_content').height(tab_content_max_h);
        }
        else {
            $('#msg_wnd').height(total_h / 2 - prompt_h - tab_bar_h);
            $('#prompt').height(prompt_h);
            $('#tab_bar').height(tab_bar_h);
            $('#tab_content').height(total_h / 2);
        }
        
        if (win_w > 960) {
            $('#middlewindow').width(960);
        }
        else {
            $('#middlewindow').width(win_w);
        }
    },

    doCancel : function() {
        this.doCloseBox();
    },

    doInputCommand : function() {
        var command = $("#popup_box :text").val();
        $("#popup_box :text").val("");
        
        history_add(command);
        HISTORY_POS = 0;
        
        sendCommand(command);
        this.doCloseBox();
    },

    showAlert : function(msg, button) {
        this.doCloseBox();
        this.createMessageBox();

        $('#input_prompt').html(text2html.parseHtml(msg));
        
        var html_button = '<div><br></div>\
                             <div>\
                                <center>\
                                    <input type="button" id="button_center" value="';
        html_button += button;
        html_button += '" class="btn btn-primary" onClick="webclient.doCloseBox()"/>\
                                </center>\
                            </div>'
        $('#input_additional').html(html_button);
        this.doSetSizes();
    },
    
    showDialogue : function(dialogues) {
        this.doCloseDialogue();
        
        try {
            if (dialogues.length == 0) {
                return;
            }
            
            this.createDialogueBox();

            if (dialogues.length == 1) {
                var content = "";
                if (dialogues[0].speaker.length > 0) {
                    content += dialogues[0].speaker + ":<br>";
                }
                content += text2html.parseHtml(dialogues[0].content);
                
                $('#input_prompt').html(content);
                
                var html_button = '<div><br></div>\
                <div>\
                <center>\
                <input type="button" id="button_center" value="';
                html_button += LS("NEXT");
                html_button += '" class="btn btn-primary"';

                if ("npc" in dialogues[0]) {
                    html_button += ' npc="' + dialogues[0].npc + '"';
                }
                html_button += ' dialogue="' + dialogues[0].dialogue + '"';
                html_button += ' sentence="' + dialogues[0].sentence + '"';
                html_button += ' onClick="commands.doDialogue(this); return false;"/>\
                </center>\
                </div>'

                $('#input_additional').html(html_button);
            }
            else {
                var content = "";
                if (dialogues[0].speaker.length > 0) {
                    content += dialogues[0].speaker + ":<br>";
                }

                for (var i in dialogues) {
                    content += '<a href="#" onclick="commands.doDialogue(this); return false;"';
               	 	content += ' npc="' + dialogues[i].npc + '"';
               		content += ' dialogue="' + dialogues[i].dialogue + '"';
                	content += ' sentence="' + dialogues[i].sentence + '"';
                    content += '">';
                    content += text2html.parseHtml(dialogues[i].content);
                    content += '</a><br>';
                }
                
                $('#input_prompt').html(content);
                
                var html_button = '<div><br></div>\
                <div>\
                <center>\
                <input type="button" id="button_center" value="SELECT ONE" class="btn btn-primary" />\
                </center>\
                </div>'
                $('#input_additional').html(html_button);
            }
        }
        catch(error) {
            this.doCloseDialogue();
        }

        this.doSetSizes();
    },
    
    createMessageBox : function() {
        var dlg = $('<div>').attr('id', 'popup_box');
        dlg.append($('<div>').attr('id', 'input_prompt'));
        dlg.append($('<div>').attr('id', 'input_additional'));

        var overlayer = $('<div>').addClass('overlayer')
                                  .attr('id', 'overlayer');
        
        $("body").prepend(overlayer);
        $("body").prepend(dlg);
    },

    createDialogueBox : function() {
        var dlg = $('<div>').attr('id', 'dialogue_box');
        dlg.append($('<div>').attr('id', 'input_prompt'));
        dlg.append($('<div>').attr('id', 'input_additional'));

        var overlayer = $('<div>').addClass('overlayer')
        .attr('id', 'overlayer');

        $("body").prepend(overlayer);
        $("body").prepend(dlg);
    },

    createInputBox : function() {
        var dlg = '<div id="popup_box">\
        <div id="close_button" class="clearfix">\
        <input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="webclient.doCloseBox()"/>\
        </div>\
        <div id="input_prompt">\
        </div>\
        <div id="input_additional">\
        </div>\
        </div>';
        
        var overlayer = '<div class="overlayer" id="overlayer"></div>';
        
        $("body").prepend(dlg + overlayer);
    },

    doCloseBox : function() {
        $('#popup_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },

    doCloseDialogue : function() {
        $('#dialogue_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },
    
    doCloseCombat : function() {
        $('#combat_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },

    doCloseMap : function() {
        $('#map_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },
    
    // show connect tabs
    showConnectTabs : function() {
        $("#tab_bar li").css("display", "none");
        
        $("#tab_connect").css("display", "");
    },
    
    // show unlogin tabs
    showUnloginTabs : function() {
        $("#tab_bar li").css("display", "none");
        
        $("#tab_register").css("display", "");
        $("#tab_login").css("display", "");
        $("#tab_command").css("display", "");

        $("#map_button").css("display", "none");
    },
    
    // show login tabs
    showLoginTabs : function() {
        $("#tab_bar").find("li").css("display", "none");
        
        $("#tab_room").css("display", "");
        $("#tab_status").css("display", "");
        $("#tab_inventory").css("display", "");
        $("#tab_skills").css("display", "");
        $("#tab_quests").css("display", "");
        $("#tab_system").css("display", "");
        $("#tab_command").css("display", "");

        $("#map_button").css("display", "");
    },
    
    unselectAllTabs : function() {
        $("#tab_bar li").removeClass("pill_active");
        $("#tab_content form").css("display", "none");
    },
    
    showPage : function(pagename) {
        this.unselectAllTabs();
        $("#tab_" + pagename).addClass("pill_active");
        $("#page_" + pagename).css("display", "");
    },
    
    onConnectionOpen: function() {
        this.showUnloginTabs();
        this.showPage("login");
        this.doSetSizes();

        webclient.doAutoLoginCheck();
    },
    
    onConnectionClose: function() {
        this.showConnectTabs();
        this.showPage("connect");
        this.doSetSizes();
    },

    doAutoLoginCheck : function() {
        setTimeout(function(){
            if($.cookie("is_save_password")) {
                $("#login_name").val($.cookie("login_name"));
                $("#login_password").val($.cookie("login_password"));
                $("#cb_save_password").attr("checked", "true");

                if($.cookie("is_auto_login")) {
                    $("#cb_auto_login").attr("checked", "true");

                    var args = {"playername" : $.cookie("login_name"),
                                "password" : $.cookie("login_password")};
                    sendCommand(JSON.stringify({"cmd" : "connect", "args" : args}));
                }
            } else {
                $("#cb_save_password").removeAttr("checked");
                $.cookie("is_auto_login", '', {expires: -1});
                $("#cb_auto_login").removeAttr("checked");
            }

            if(!$.cookie("is_auto_login")) {
                $("#cb_auto_login").removeAttr("checked");
            }
        }, 1);
    },
}

// Input jQuery callbacks
$(document).unbind("keydown");

$(window).ready(function(){
    webclient.showUnloginTabs();
    webclient.showPage("login");
    webclient.doSetSizes();
});

// Callback function - called when the browser window resizes
$(window).unbind("resize");
$(window).resize(webclient.doSetSizes);
