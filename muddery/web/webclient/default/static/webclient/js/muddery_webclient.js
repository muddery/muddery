/*
Muddery webclient (javascript component)
*/

var webclient = {
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
                else if (key == "look_obj") {
                    this.displayLookObj(data[key]);
                }
                else if (key == "inventory") {
                    this.displayInventory(data[key]);
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
                content += "<div id='room_cmds'>Actions:</div>";
            }
        }
        
        if ("exits" in data) {
            if (data["exits"].length > 0) {
                content += "<div id='room_exits'>Exits:"
                // add exits
                for (var i in data["exits"]) {
                    try {
                        var exit = data["exits"][i];
                        element = " <a href='#' onclick='commands.doGotoLink(this); return false;' ";
                        element += "dbref='" + exit["dbref"] + "'>";
                        element += exit["name"];
                        element += "</a>";
                        content += element;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }
        
        if ("things" in data) {
            if (data["things"].length > 0) {
                content += "<div id='room_things'>Things:"
                // add things
                for (var i in data["things"]) {
                    try {
                        var thing = data["things"][i];
                        element = " <a href='#' onclick='commands.doLookLink(this); return false;' ";
                        element += "dbref='" + thing["dbref"] + "'>";
                        element += thing["name"];
                        element += "</a>";
                        content += element;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }

        if ("npcs" in data) {
            if (data["npcs"].length > 0) {
                content += "<div id='room_npcs'>NPCs:"
                // add npcs
                for (var i in data["npcs"]) {
                    try {
                        var npc = data["npcs"][i];
                        element = " <a href='#' onclick='commands.doLookLink(this); return false;' ";
                        element += "dbref='" + npc["dbref"] + "'>";
                        element += npc["name"];
                        element += "</a>";
                        content += element;
                    }
                    catch(error) {
                    }
                }
                content += "</div>";
            }
        }

        if ("players" in data) {
            if (data["players"].length > 0) {
                content += "<div id='room_players'>Players:"
                // add players
                for (var i in data["players"]) {
                    try {
                        var player = data["players"][i];
                        element = " <a href='#' onclick='commands.doLookLink(this); return false;' ";
                        element += "dbref='" + player["dbref"] + "'>";
                        element += player["name"];
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
        
        // add commands
        if ("cmds" in data) {
            var room_cmds = $("#room_cmds");
            for (var i in data["cmds"]) {
                try {
                    var cmd = data["cmds"][i];
                    element = " <a href='#' onclick='commands.doCommandLink(this); return false;'>"
                    element += cmd["name"];
                    element += "</a>";
                    room_cmds.append(element);
                    
                    room_cmds.find("a:last").data({"cmd": cmd["cmd"], "args": cmd["args"]});
                }
                catch(error) {
                }
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
                content += "<div id='object_cmds'>Actions:</div>";
            }
        }

        page.html(content);
        
        // add commands
        if ("cmds" in data) {
            var object_cmds = $("#object_cmds");
            for (var i in data["cmds"]) {
                try {
                    var cmd = data["cmds"][i];
                    element = " <a href='#' onclick='commands.doClick(this); return false;'>"
                    element += cmd["name"];
                    element += "</a>";
                    object_cmds.append(element);
                    
                    object_cmds.find("a:last").data({"cmd": cmd["cmd"], "args": cmd["args"]});
                }
                catch(error) {
                }
            }
        }
        
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
        var page = $("#page_inventory");
        
        var content = "<table class='tab_inventory'>";
        content += "<thead><tr><th>NAME</th><th>DESC</th></tr></thead>";
        var element = "";

        for (var i in data) {
            try {
                var obj = data[i];
                element = "<tbody><tr><td>";
                element += " <a href='#' onclick='commands.doLookLink(this); return false;' "
                element += "dbref='" + obj["dbref"] + "'>";
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

    onLogin : function(data) {
        $("#msg_wnd").empty();
        this.showLoginTabs();
        this.showPage("room");
    },
    
    onLogout : function(data) {
        $("#msg_wnd").empty();
        this.showUnloginTabs();
        this.showPage("login");
        
        //reconnect, show the connection screen
        webclient_init();
    },

    doSetSizes : function() {
        // Sets the size of the message window
        var win_h = $(window).innerHeight();
        var win_w = $(window).innerWidth();
        var close_h = $('#close_button').outerHeight(true);
        var prom_h = $('#input_prompt').outerHeight(true);
        var add_h = $('#input_additional').outerHeight(true);
        $('#popup_box').height(close_h + prom_h + add_h);
        
        var inp_h = $('#popup_box').outerHeight(true);
        var inp_w = $('#popup_box').outerWidth(true);
        //$("#wrapper").css({'height': win_h - inp_h - 1});
        $('#popup_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

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
        var total_h = middle_h - 2;
        var tab_bar_h = 30;
        var tab_content_max_h = 360;
        if (total_h + tab_bar_h > tab_content_max_h * 2) {
            $('#msg_wnd').height(middle_h - tab_bar_h - tab_content_max_h - 2);
            $('#tab_bar').height(tab_bar_h);
            $('#tab_content').height(tab_content_max_h);
        }
        else {
            $('#msg_wnd').height(total_h / 2 - tab_bar_h);
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
        $("#tab_inventory").css("display", "");
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
