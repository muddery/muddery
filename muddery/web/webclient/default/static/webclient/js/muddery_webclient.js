/*
Muddery webclient (javascript component)
*/

var webclient = {
    _self_dbref: null,

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
                else if (key == "show_combat") {
                    this.displayCombat(data[key]);
                }
                else if (key == "login") {
                    this.onLogin(data[key]);
                }
                else if (key == "logout") {
                    this.onLogout(data[key]);
                }
                else {
                    this.displayMsg(data[key]);
                }
            }
            catch(error) {
                this.displayErr("Data error.");
            }
        }
    },

    displayMsg : function(data) {
        this.displayTextMsg("msg", text2html.parseHtml(data));
    },
        
    displayAlert : function(data) {
        try {
            var msg = "";
            var button = "OK";
            
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
        msg_wnd.append("<div class='msg "+ type +"'>"+ msg +"</div>");
        
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
        else if (tab_name.length > 10) {
            tab_name = tab_name.substring(0, 8) + "...";
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
        content += "<div><span class='cyan'>\>\>\>\>\> " + element + " \<\<\<\<\<</span></div>";

        // add room's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            content += "<div>" + element + "</div>";
        }
        catch(error) {
        }

        content += "<div><br></div>";
        
        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                content += "<div id='room_cmds'>Commands:"
                // add cmds
                for (var i in data["cmds"]) {
                    try {
                        var cmd = data["cmds"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='" + cmd["cmd"] + "'";
                        element += " cmd_args='" + cmd["args"] + "'>";
                        element += cmd["name"];
                        element += "</a>";
                        content += element;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        var empty = true;
        if ("exits" in data) {
            if (data["exits"].length > 0) {
                content += "<div id='room_exits'>Exits:"
                // add exits
                for (var i in data["exits"]) {
                    try {
                        var exit = data["exits"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='look'";
                        element += " cmd_args='" + exit["dbref"] + "'";
                        element += " dbref='" + exit["dbref"] + "'>";
                        element += exit["name"];
                        element += "</a>";
                        content += element;
                        empty = false;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        if (empty) {
            content += "<div id='room_exits' style='display:none'>Exits:</div>"
        }
        
        empty = true;
        if ("things" in data) {
            if (data["things"].length > 0) {
                content += "<div id='room_things'>Things:"
                // add things
                for (var i in data["things"]) {
                    try {
                        var thing = data["things"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='look'";
                        element += " cmd_args='" + thing["dbref"] + "'";
                        element += " dbref='" + thing["dbref"] + "'>";
                        element += thing["name"];
                        element += "</a>";
                        content += element;
                        empty = false;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        if (empty) {
            content += "<div id='room_things' style='display:none'>Things:</div>"
        }

        empty = true;
        if ("npcs" in data) {
            if (data["npcs"].length > 0) {
                content += "<div id='room_npcs'>NPCs:"
                // add npcs
                for (var i in data["npcs"]) {
                    try {
                        var npc = data["npcs"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='look'";
                        element += " cmd_args='" + npc["dbref"] + "'";
                        element += " dbref='" + npc["dbref"] + "'>";
                        element += npc["name"];
                        element += "</a>";
                        
                        if (npc["finish_quest"]) {
                            element += "[!]";
                        }
                        else if (npc["provide_quest"]) {
                            element += "[?]";
                        }

                        content += element;
                        empty = false;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        if (empty) {
            content += "<div id='room_npcs' style='display:none'>NPCs:</div>"
        }

        empty = true;
        if ("players" in data) {
            if (data["players"].length > 0) {
                content += "<div id='room_players'>Players:"
                // add players
                for (var i in data["players"]) {
                    try {
                        var player = data["players"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='look'";
                        element += " cmd_args='" + player["dbref"] + "'";
                        element += " dbref='" + player["dbref"] + "'>";
                        element += player["name"];
                        element += "</a>";
                        content += element;
                        empty = false;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        if (empty) {
            content += "<div id='room_players' style='display:none'>Players:</div>"
        }
        
        page.html(content);
    },
    
    displayObjMovedIn : function(data) {
        for (var key in data) {
            var page = $("#room_" + key);
            page.css("display", "");

            for (var i in data[key]) {
                try {
                    var obj = data[key][i];
                    element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                    element += " cmd_name='look'";
                    element += " cmd_args='" + obj["dbref"] + "'";
                    element += " dbref='" + obj["dbref"] + "'>";
                    element += obj["name"];
                    element += "</a>";
                    page.append(element);
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
    
    displayLookObj : function(data) {
        this.doCloseBox();
        this.createMessageBox();
        
        var page = $("#input_prompt");

        // object's info
        var content = "";
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
        content += "<div><center><span class='lime'>\>\>\> " + element + " \<\<\<<center></span></div>";

        // add object's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            content += "<div>" + element + "</div>";
        }
        catch(error) {
        }

        content += "<div><br></div>";

        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                content += "<div id='object_cmds'>Actions:"
                // add cmds
                for (var i in data["cmds"]) {
                    try {
                        var cmd = data["cmds"][i];
                        element = " <a href='#' onclick='webclient.doCloseBox(); commands.doCommandLink(this); return false;'";
                        element += " cmd_name='" + cmd["cmd"] + "'";
                        element += " cmd_args='" + cmd["args"] + "'>";
                        element += cmd["name"];
                        element += "</a>";
                        content += element;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }

        page.html(content);
        
        // button
        var html_button = '<div><br></div>\
                             <div>\
                                <center>\
                                    <input type="button" id="button_center" value="OK" class="btn btn-primary" onClick="webclient.doCloseBox()"/>\
                                </center>\
                            </div>'
        $('#input_additional').html(html_button);
        this.doSetSizes();
    },
    
    displayInventory : function(data) {
        // display player's inventory
        var page = $("#page_inventory");
        
        var content = "<table class='tab_inventory'>";
        content += "<thead><tr><th>NAME</th><th>NUM</th><th>DESC</th></tr></thead>";
        var element = "";

        for (var i in data) {
            try {
                var obj = data[i];
                element = "<tbody><tr><td>";
                element += " <a href='#' onclick='commands.doCommandLink(this); return false;'"
                element += " cmd_name='look'";
                element += " cmd_args='" + obj["dbref"] + "'>";
                element += obj["name"];
                element += "</a></td>";

                element += "<td>";
                element += obj["number"];
                if ("equipped" in obj)
                    if (obj["equipped"]) {
                        element += " (equipped)";
                    }

                element += "</td>";

                element += "<td>";
                element += obj["desc"];
                element += "</td></tr></tbody>";
                
                content += element;
            }
            catch(error) {
            }
        }
        
        content += "</table>";
        
        page.html(content);
    },

    displaySkills : function(data) {
        // display player's skills
        var page = $("#page_skills");
        
        var content = "<table class='tab_skills'>";
        content += "<thead><tr><th>NAME</th><th>DESC</th></tr></thead>";
        var element = "";

        for (var i in data) {
            try {
                var obj = data[i];
                element = "<tbody><tr><td>";
                element += " <a href='#' onclick='commands.doCommandLink(this); return false;'"
                element += " cmd_name='look'";
                element += " cmd_args='" + obj["dbref"] + "'>";
                element += obj["name"];
                element += "</a></td>";
                element += "<td>";
                element += obj["desc"];
                element += "</td></tr></tbody>";
                
                content += element;
            }
            catch(error) {
            }
        }
        
        content += "</table>";
        
        page.html(content);
    },

    displayQuests : function(data) {
        // display player's quests
        var page = $("#page_quests");
        
        var content = "<table class='tab_quests'>";
        content += "<thead><tr><th>名称</th><th>说明</th><th>目标</th></tr></thead>";
        var element = "";

        for (var i in data) {
            try {
                var quest = data[i];
                element = "<tbody><tr><td>";
                element += " <a href='#' onclick='commands.doCommandLink(this); return false;'"
                element += " cmd_name='look'";
                element += " cmd_args='" + quest["dbref"] + "'>";
                element += quest["name"];
                element += "</a></td>";
                element += "<td>";
                element += quest["desc"];
                element += "</td>";
                element += "<td>";

                var objectives = ""
                for (var o in quest["objectives"]) {
                    if (objectives.length > 0) {
                        objectives += "<br>";
                    }
                    
                    var obj = quest["objectives"][o];
                    objectives += obj["target"] + obj["object"];
                    objectives += obj["achieved"] + "/" + obj["total"];
                }
                
                element += objectives;
                element += "</td></tr></tbody>";
                
                content += element;
            }
            catch(error) {
            }
        }
        
        content += "</table>";
        
        page.html(content);
    },

    displayGetObject : function(data) {
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
                    content += "You got:<br>";
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
                    content += "You can not get:<br>";
                    first = false;
                }
                content += element;
                count += 1;
            }
        }
        catch(error) {
        }
        
        if (count == 0) {
            content = "You got nothing.";
        }

        page.html(content);
        
        // button
        var html_button = '<div><br></div>\
                             <div>\
                                <center>\
                                    <input type="button" id="button_center" value="OK" class="btn btn-primary" onClick="webclient.doCloseBox()"/>\
                                </center>\
                            </div>'
        $('#input_additional').html(html_button);
        this.doSetSizes();
    },

    displayCombat : function(data) {
        this.doCloseBox();
        this.doCloseCombat();

        $('<div>').addClass('overlayer').attr('id', 'overlayer').prependTo($("body"));

        var box = $('<div>').attr('id', 'combat_box')
        
        for (var i in data["characters"]) {
            var fighter = data["characters"][i];
            var div = $('<div>').attr('id', fighter["dbref"])
                                .text(fighter["name"])
                                .data('hp', fighter["hp"])
                                .data('max_hp', fighter["max_hp"])
                                .data('dbref', fighter["dbref"]);
            $('<div>').addClass('hp').text(fighter["hp"] + '/' + fighter["max_hp"]).appendTo(div);
            
            if (fighter["dbref"] == this._self_dbref) {
                div.addClass("fighter_self");
            }
            else {
                div.addClass("fighter_enemy");
                this._current_target = fighter["dbref"];
            }
            
            div.appendTo(box);
        }

        for (var i in data["commands"]) {
            var command = data["commands"][i];
            var button = $('<input type="button" class="btn btn-combat">')
                            .css({'left': 20 + i * 60})
                            .attr('cmd_name', command["cmd"])
                            .attr('onclick', 'commands.doCommandAttack(this); return false;')
                            .val(command["name"]);

            button.appendTo(box);
        }

        box.prependTo($("body"));
        
        this.doSetSizes();
    },

    displayStatus : function(data) {
        // refresh prompt bar
        var bar = $("#prompt_bar");
        var prompt = "";
        var element = "";
        
        try {
            element = "<span class='white'> HP: ";
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
            element = "<div><span class='white'> LEVEL: ";
            element += data["level"].toString();
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
            element = "<div>Equipments: ";
            for (position in data) {
                element += "<br>";
                element += "&nbsp;&nbsp;" + position + ": ";
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
        this._self_dbref = data["dbref"];

        // show login UI
        $("#msg_wnd").empty();
        this.showLoginTabs();
        this.showPage("room");
    },
    
    onLogout : function(data) {
        // show unlogin UI
        $("#msg_wnd").empty();
        $("#prompt_bar").empty();
        this.showUnloginTabs();
        this.showPage("login");
        
        //reconnect, show the connection screen
        webclient_init();
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

        // combat box
        var inp_h = $('#combat_box').outerHeight(true);
        var inp_w = $('#combat_box').outerWidth(true);
        $('#combat_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

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
        var tab_bar_h = 30;
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
        this.doCloseBox();
        
        try {
            if (dialogues.length == 0) {
                return;
            }
            
            this.createMessageBox();

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
                <input type="button" id="button_center" value="NEXT" class="btn btn-primary"';

                html_button += ' npc="' + dialogues[0].npc + '"';
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
            this.doCloseBox();
        }

        this.doSetSizes();
    },
    
    createMessageBox : function() {
        var dlg = '<div id="popup_box">\
        <div id="input_prompt">\
        </div>\
        <div id="input_additional">\
        </div>\
        </div>';
        
        var overlayer = '<div class="overlayer" id="overlayer"></div>';
        
        $("body").prepend(dlg + overlayer);
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
    
    doCloseCombat : function() {
        $('#combat_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },
    
    // show unlogin tabs
    showUnloginTabs : function() {
        $("#tab_bar li").css("display", "none");
        
        $("#tab_login").css("display", "");
        $("#tab_command").css("display", "");
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
    
    get_current_target: function() {
        return this._current_target;
    },
}

// Input jQuery callbacks
$(document).unbind("keydown");

$(window).ready(function(){
    webclient.showUnloginTabs();
    webclient.showPage("login");
});

// Callback function - called when the browser window resizes
$(window).unbind("resize");
$(window).resize(webclient.doSetSizes);
