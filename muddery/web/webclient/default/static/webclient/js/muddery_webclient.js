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

            popupmgr.showAlert(msg, button);
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
        var tab = $("#tab_scene a");
        var box = $("#box_scene");

        ///////////////////////
        // set scene box
        ///////////////////////
        
        var content = "";
        var element = "";
        
        // add room's dbref
        var dbref = "";
        if ("dbref" in data) {
            dbref = data["dbref"];
            box.data("dbref", dbref);
        }
        
        // add room's name
        try {
            element = data["name"];
        }
        catch(error) {
            element = tab_name;
        }
        box.empty();
        uimgr.divRoomTabName(element).appendTo(box);

        // add room's desc
        try {
            element = text2html.parseHtml(data["desc"]);
            uimgr.divEmpty(element).appendTo(box);
        }
        catch(error) {
        }

        uimgr.divBR().appendTo(box);

        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                uimgr.divRoomCmds(data["cmds"]).appendTo(box);
            }
        }

        var empty = true;
        if ("exits" in data) {
            if (data["exits"].length > 0) {
                uimgr.divRoomExits(data["exits"]).appendTo(box);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomExits("").appendTo(box);
        }

        empty = true;
        if ("things" in data) {
            if (data["things"].length > 0) {
                uimgr.divRoomThings(data["things"]).appendTo(box);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomThings("").appendTo(box);
        }

        empty = true;
        if ("npcs" in data) {
            if (data["npcs"].length > 0) {
                uimgr.divRoomNpcs(data["npcs"]).appendTo(box);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomNpcs("").appendTo(box);
        }

        empty = true;
        if ("players" in data) {
            if (data["players"].length > 0) {
                uimgr.divRoomPlayers(data["players"]).appendTo(box);
                empty = false;
            }
        }

        if (empty) {
            uimgr.divRoomPlayers("").appendTo(box);
        }
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

        popupmgr.doCloseBox();
        popupmgr.createMessageBox();

        $('#popup_header').html('displayLookObj');
        var page = $('#popup_body');
        var footer = $('#popup_footer');

        var title = $('<div>').addClass('clearfix')
                              .appendTo(page);

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

        uimgr.divBR().appendTo(footer);

        if ("cmds" in data) {
            if (data["cmds"].length > 0) {
                uimgr.divObjectCmds(data["cmds"]).appendTo(footer);
            } else {
                var html_button = $('<button>')
                    .attr('class', 'btn btn-default')
                    .attr('type', 'button')
                    .attr('data-dismiss', 'modal')
                    .text("关闭")
                    .attr('id', 'button_center')
                    .attr('onClick', 'popupmgr.doCloseBox()');
                footer.html(html_button);
            }
        }

        // button
        /*
        var html_button = '<div><br></div>\
                             <div>\
                                <center>\
                                    <input type="button" id="button_center" value="OK" class="btn btn-primary" onClick="popupmgr.doCloseBox()"/>\
                                </center>\
                            </div>'
        $('#input_additional').html(html_button);
        */
        webclient.doSetSizes();
    },
    
    displayInventory : function(data) {
        // display player's inventory
        var page = $("#box_inventory").html("");
        uimgr.tableInventory(data).appendTo(page);
    },

    displaySkills : function(data) {
        // display player's skills
        var page = $("#box_skill").html("");
        uimgr.tableSkills(data).appendTo(page);
    },

    displayQuests : function(data) {
        // display player's quests
        var page = $("#box_quest").html("");
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
        popupmgr.doCloseBox();
        popupmgr.createMessageBox();

        $('#popup_header').html('displayGetObjectBox');

        var page = $("#popup_body");

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
        $('#popup_footer').append(br);

        var div = $("<div>");
        var html_button = $("<button>").addClass("btn btn-default")
        							  .attr("type", "button")
        							  .attr("id", "button_center")
                                      .attr('data-dismiss', 'modal')
        							  .attr("onClick", "popupmgr.doCloseBox()")
        							  .text(LS("OK"))
        							  .appendTo(div);

        $('#popup_footer').append(div);
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
        var block = $("#box_status");
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
        var block = $("#box_equipment");
        var content = "";

        try {
            element = "<div>";
            for (position in data) {
                element += "&nbsp;&nbsp;" + position + LS(": ");
                if (data[position] != null) {
                    element += " <a href='#' onclick='commands.doCommandLink(this); return false;'"
                    element += " cmd_name='look'";
                    element += " cmd_args='" + data[position].dbref + "'>";
                    element += data[position].name;
                    element += "</a>"
                }
                element += "<br>";
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
        popupmgr.showDialogue(data);
    },

    onLogin : function(data) {
        // show login UI
        $("#msg_wnd").empty();
        this.showLoginTabs();
        this.showPage("scene");
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

        var head_h = $('header').outerHeight(true);
        var wrapper_h = win_h - head_h - 30;

        $('#wrapper').height(wrapper_h);

        var prompt_h = 18;
        var tab_bar_h = 50;
        var msg_wnd_h = wrapper_h / 3;
        var tab_content_h = wrapper_h / 3;
        $('#msg_wnd').height(msg_wnd_h);
        $('#prompt').height(prompt_h);
        $('#tab_bar').height(tab_bar_h);
        $('#tab_content').height(tab_content_h);

        if (win_w >= 960) {
            $('#middlewindow').width(960 - 20);
        }
        else {
            $('#middlewindow').width(win_w - 20);
        }
    },

    doCancel : function() {
        popupmgr.doCloseBox();
    },

    doInputCommand : function() {
        var command = $("#popup_box :text").val();
        $("#popup_box :text").val("");
        
        history_add(command);
        HISTORY_POS = 0;
        
        sendCommand(command);
        popupmgr.doCloseBox();
    },

    createInputBox : function() {
        var dlg = '<div id="popup_box">\
        <div id="close_button" class="clearfix">\
        <input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="popupmgr.doCloseBox()"/>\
        </div>\
        <div id="input_prompt">\
        </div>\
        <div id="input_additional">\
        </div>\
        </div>';
        
        var overlayer = '<div class="overlayer" id="overlayer"></div>';
        
        $("body").prepend(dlg + overlayer);
    },

    // hide all tabs
    hideTabs : function() {
        $("#tab_pills").children().css("display", "none");
    },

    // show connect tabs
    showConnectTabs : function() {
        this.hideTabs();

        $("#tab_connect").css("display", "");
    },
    
    // show unlogin tabs
    showUnloginTabs : function() {
        this.hideTabs();

        $("#tab_register").css("display", "");
        $("#tab_login").css("display", "");
        $("#tab_command").css("display", "");

        $("#map_button").css("display", "none");
    },
    
    // show login tabs
    showLoginTabs : function() {
        this.hideTabs();

        $("#tab_scene").css("display", "");
        $("#tab_character").css("display", "");
        $("#tab_quest").css("display", "");
        $("#tab_map").css("display", "");
        $("#tab_system").css("display", "");
        $("#tab_command").css("display", "");

        $("#map_button").css("display", "");
    },
    
    unselectAllTabs : function() {
        $("#tab_bar li")
            .removeClass("active")
            .removeClass("pill_active");
        $("#tab_content").children().css("display", "none");
    },
    
    showPage : function(pagename) {
        this.unselectAllTabs();
        $("#tab_" + pagename)
            .addClass("active")
            .addClass("pill_active");
        $("#box_" + pagename).css("display", "");
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

// Callback function - called when the browser window resizes
$(window).unbind("resize");
$(window).resize(webclient.doSetSizes);