/*
Muddery webclient (javascript component)
*/

var webclient = {
 	onText: function(args, kwargs) {
 	    for (index in args) {
 		    webclient.doShow("out", args[index]);
 		}
 	},
 	
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
                	var msg = text2html.parseHtml(data[key]);
                    controller.displayMsg(msg);
                }
                else if (key == "alert") {
              		controller.showAlert(data[key]);
                }
                else if (key == "out") {
                    controller.displayMsg(data[key], "out");
                }
                else if (key == "err") {
                    controller.displayMsg(data[key]);
                }
                else if (key == "sys") {
                    controller.displayMsg(data[key], "sys");
                }
                else if (key == "debug") {
                	controller.displayMsg(data[key], "debug");
                }
                else if (key == "prompt") {
                	controller.displayMsg(data[key], "prompt");
                }
                else if (key == "settings") {
                    settings.set(data[key]);
                }
                else if (key == "look_around") {
                    controller.setScene(data[key]);
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
                    var obj = data[key];
        			controller.showObject(obj["name"], obj["icon"], obj["desc"], obj["cmds"]);
                }
                else if (key == "dialogues_list") {
                    this.displayDialogue(data[key]);
                }
                else if (key == "status") {
                    var status = data[key];
                    controller.setStatus(status["level"],
                                         status["exp"],
                                         status["max_exp"],
                                         status["hp"],
                                         status["max_hp"],
                                         status["attack"],
                                         status["defence"]);
                }
                else if (key == "equipments") {
			        controller.setEquipments(data[key]);
                }
                else if (key == "inventory") {
                    controller.setInventory(data[key]);
                }
                else if (key == "skills") {
                    controller.setSkills(data[key]);
                }
                else if (key == "quests") {
                	controller.setQuests(data[key]);
                }
                else if (key == "get_object") {
                    controller.showGetObjects(data[key]["accepted"], data[key]["rejected"]);
                }
                else if (key == "joined_combat") {
                    controller.showCombat(data[key]);
                }
                else if (key == "left_combat") {
                    controller.closeCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    controller.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                	var info = data[key];
                    controller.setCombatInfo(info["desc"], info["characters"]);
                }
                else if (key == "combat_commands") {
                    controller.setCombatCommands(data[key]);
                }
                else if (key == "skill_cd") {
                	var skill_cd = data[key];
                    controller.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                }
                else if (key == "skill_result") {
                    controller.setSkillResult(data[key]);
                }
                else if (key == "get_exp") {
                    controller.showGetExp(data[key])
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
                else if (key == "shop") {
                    this.displayShop(data[key])
                }
                else {
                    controller.displayMsg(data[key]);
                }
            }
            catch(error) {
                console.log(key, data[key])
                console.error(error.message);
            }
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
                    var dbref = data[key][i]["dbref"];
                    if (data_handler.dialogue_target == dbref) {
                        // If the player is talking to it, close the dialog window.
                        popupmgr.doCloseDialogue();
                    }
                    page.find("a[dbref=" + dbref + "]").remove();
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

    displayDialogue : function(data) {
        if (data.length == 0) {
            controller.doClosePopupBox();
        }
        else {
            if ($('#combat_box').length > 0) {
                // has combat box
                combat.setDialogue(data);
            }
            else {
                data_handler.dialogues_list = data;
                dialogues = data_handler.dialogues_list.shift();
                if (dialogues.length > 0) {
                    data_handler.dialogue_target = dialogues[0].npc;
                }

                controller.showDialogue(dialogues);
            }
        }
    },

    displayShop: function(data) {
        data_handler.shop_data = data;
        controller.setShop(data["name"], data["icon"], data["desc"], data["goods"]);
    },

    onLogin : function(data) {
        // show login UI
        controller.clearMsgWindow();

        controller.clearPromptBar();
        $("#prompt_content").show();

        this.showLoginTabs();
        this.showContent("scene");
    },
    
    onLogout : function(data) {
        // show unlogin UI
        controller.clearMsgWindow();
        $("#prompt_content").hide();
        this.showUnloginTabs();
        this.showPage("login");
        
        //reconnect, show the connection screen
        Evennia.connect();
    },
    
    onPuppet: function(data) {
        data_handler.character_dbref = data["dbref"];
        data_handler.character_name = data["name"];

        controller.setInfo(data["name"], data["icon"]);
    },

    doSetSizes: function() {
        webclient.doSetWindowSize();
        webclient.doSetVisiblePopupSize();
    },

    doSetWindowSize: function() {
        // Sets the size of the message window
        var win_h = $(window).innerHeight();
        var win_w = $(window).innerWidth();

        //var head_h = $('header').outerHeight(true);
        var head_h = 20;
        $('#header').height(head_h);

        var wrapper_h = win_h - head_h - 20;
        $('#wrapper').height(wrapper_h);

        var margin_h = 55
        var prompt_h = 18;
        var tab_bar_h = 32;
        var tab_content_h = (wrapper_h - prompt_h - tab_bar_h - margin_h) * 0.7;
        $('#prompt_bar').height(prompt_h);
        $('#tab_bar').height(tab_bar_h);
        $('#tab_content').height(tab_content_h);

        tab_content_h = $('#tab_content').height();
        var msg_wnd_h = wrapper_h - prompt_h - tab_bar_h - margin_h - tab_content_h;
        $('#msg_wnd').height(msg_wnd_h);

        if (win_w >= 960) {
            $('#middlewindow').width(960 - 20);
        }
        else {
            $('#middlewindow').width(win_w - 20);
        }
        
        webclient.doChangeVisibleFrameSize();
    },

    doSetVisiblePopupSize: function() {
        var popup_content = $("#popup_content");
        var frame = popup_content.find("iframe:visible:first");
        if (frame.length == 0) {
            return;
        }

        var width = popup_content.width();
        frame.innerWidth(popup_content.width());
        frame.height(0);
        
        var frame_body = frame[0].contentWindow.document.body;
		frame.height(frame_body.scrollHeight);

        // model dialogue
        var win_h = $(window).innerHeight();
        var dlg = $('#box_pop');
        if (dlg.length > 0) {
            dlg.css('top', (win_h - dlg.height()) / 2);
        }
    },
    
    doChangeVisibleFrameSize: function() {
		var frame = $("#tab_content iframe:visible");
		this.doChangeFrameSize(frame);
    },

	doChangeFrameSize: function(frame) {
		var tab_content = $("#tab_content");

    	frame.width(tab_content.width());
    	frame.height(tab_content.height() - 5);
    },

    doCancel: function() {
        popupmgr.doCloseBox();
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
    },
    
    // show login tabs
    showLoginTabs : function() {
        this.hideTabs();

        $("#tab_scene").css("display", "");
        $("#tab_character").css("display", "");
        if (settings.show_social_box) {
        	$("#tab_social").css("display", "");
        }
        $("#tab_map").css("display", "");
        $("#tab_system").css("display", "");
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
    
    hideAllContents: function() {
        $("#tab_bar li")
            .removeClass("active")
            .removeClass("pill_active");

    	$("#tab_content").children().hide();
    },
    
    showContent: function(frame_name) {
        this.hideAllContents();
        
        $("#tab_" + frame_name)
            .addClass("active")
            .addClass("pill_active");

		var frame = $("#frame_" + frame_name);
		this.doChangeFrameSize(frame);
        frame.show();
    },
    
    onConnectionOpen: function() {
        controller.clearMsgWindow();
        $("#prompt_content").hide();
        webclient.showUnloginTabs();
        webclient.showContent("login");

        webclient.doAutoLoginCheck();
    },
    
    onConnectionClose: function() {
        webclient.showConnectTabs();
        webclient.showContent("connect");

        // close all popup windows
        combat.closeCombat();
        popupmgr.doCloseBox();
        popupmgr.doCloseDialogue();
        popupmgr.doCloseMap();
        popupmgr.doCloseShop();

        // show message
        controller.showMessage(_("Message"), _("The client connection was closed cleanly."));
    },

    doAutoLoginCheck : function() {
        setTimeout(function(){
            if($.cookie("is_save_password")) {
                $("#login_name").val($.cookie("login_name"));
                $("#login_password").val($.cookie("login_password"));
                $("#cb_save_password").attr("checked", "true");

                if($.cookie("is_auto_login")) {
                    $("#cb_auto_login").attr("checked", "true");
                    commands.doLogin();
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
//$(document).unbind("keydown");

// Callback function - called when the browser window resizes
//$(window).unbind("resize");
//$(window).resize(webclient.doSetSizes);

$(window).ready(function(){
    webclient.showUnloginTabs();
    webclient.showContent("login");
    webclient.doSetSizes();
});

// Event when client finishes loading
$(document).ready(function() {
    // Event when client window changes
    $(window).bind("resize", webclient.doSetSizes);

    // This is safe to call, it will always only
    // initialize once.
    Evennia.init();
    // register listeners
    Evennia.emitter.on("text", webclient.onText);
    //Evennia.emitter.on("prompt", onPrompt);
    //Evennia.emitter.on("default", onDefault);
    Evennia.emitter.on("connection_close", webclient.onConnectionClose);
    // silence currently unused events
    Evennia.emitter.on("connection_open", webclient.onConnectionOpen);
    //Evennia.emitter.on("connection_error", onSilence);

    webclient.doSetSizes();
    // set an idle timer to send idle every 3 minutes,
    // to avoid proxy servers timing out on us
    setInterval(function() {
        // Connect to server
        if (Evennia.isConnected()) {
            Evennia.msg("text", ["idle"], {});
        }
    },
    60000*3
    );
});
