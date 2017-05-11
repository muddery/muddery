
var controller = {

	// message window
	clearMsgWindow: function() {
	    $("#msg_wnd>div:not(.template)").remove();
	},

	displayMsg : function(msg, type) {
        var msg_wnd = $("#msg_wnd");
        if (msg_wnd.length > 0) {
            msg_wnd.stop(true);
            msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
        }
        
        if (!type) {
        	type = "normal";
        }

		var item_template = msg_wnd.find("div.template");
		var item = item_template.clone()
			.removeClass("template")
			.addClass("msg-" + type)
        	.html(msg)
            .appendTo(msg_wnd);

        // remove old messages
        var divs = msg_wnd.find("div:not(.template)");
        var max = 40;
        var size = divs.size();
        if (size > max) {
            divs.slice(0, size - max).remove();
        }
        
        // scroll message window to bottom
        // $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
        msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
    },
    
	// popup boxes
	showAlert: function(message) {
        this.showMessage(_("Message"), message);
	},

	showMessage: function(header, content, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_message";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setMessage(header, content, commands);

        this.showFrame(frame_id);
	},

	showObject: function(dbref, name, icon, desc, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_object";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setObject(dbref, name, icon, desc, commands);

        this.showFrame(frame_id);
	},

    setDialogueList: function(data) {
        if (data.length == 0) {
            this.doClosePopupBox();
        }
        else {
            if ($("#frame_combat").is(":visible")) {
                // show dialogue after a combat
        		var frame_id = "#frame_combat_result";
				var result_ctrl = this.getFrameController(frame_id);
				result_ctrl.setDialogue(data);
            }
            else {
                data_handler.dialogues_list = data;
                dialogues = data_handler.dialogues_list.shift();
                this.showDialogue(dialogues);
            }
        }
    },

    showDialogue: function(dialogues) {
        this.doClosePopupBox();

        var frame_id = "#frame_dialogue";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setDialogues(dialogues, data_handler.getEscapes());

        this.showFrame(frame_id);
    },
    
    showShop: function(name, icon, desc, goods) {
    	this.doClosePopupBox();

        var frame_id = "#frame_shop";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setShop(name, icon, desc, goods);

        this.showFrame(frame_id);
    },
    
    openShop: function() {
    	this.doClosePopupBox();
        this.showFrame("#frame_shop");
    },
    
    showGoods: function(dbref, name, number, icon, desc, price, unit) {
		this.doClosePopupBox();

        var frame_id = "#frame_goods";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setGoods(dbref, name, number, icon, desc, price, unit);

        this.showFrame(frame_id);
    },
    
    showGetObjects: function(accepted, rejected, combat) {
        // show accepted objects
        try {
            var first = true;
            for (var key in accepted) {
                if (first) {
                    this.displayMsg(LS("You got:"));
                    first = false;
                }
                this.displayMsg(key + ": " + accepted[key]);
            }
        }
        catch(error) {
        	console.error(error.message);
        }

        // show rejected objects
        try {
            var first = true;
            for (var key in rejected) {
                if (first) {
                    this.displayMsg(LS("You can not get:"));
                    first = false;
                }
                this.displayMsg(key + ": " + rejected[key]);
            }
        }
        catch(error) {
        	console.error(error.message);
        }

        if (combat) {
        	var frame_id = "#frame_combat_result";
			var frame_ctrl = this.getFrameController(frame_id);
        	frame_ctrl.setGetObjects(accepted, rejected);
        }
        else {
            // If not in combat.
            var popup_box = $('#popup_box');
            if (popup_box.length == 0) {
                // If there is no other boxes, show getting object box.
                this.popupGetObjects(accepted, rejected);
            }
        }
    },
    
    popupGetObjects: function(accepted, rejected) {
    	this.doClosePopupBox();

        var frame_id = "#frame_get_objects";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setGetObjects(accepted, rejected);

        this.showFrame(frame_id);
    },
    
    showCombat: function(combat) {     
    	this.doClosePopupBox();

        var combat_id = "#frame_combat";
        var combat_ctrl = this.getFrameController(combat_id);
        combat_ctrl.reset(data_handler.skill_cd_time);
        
        var result_id = "#frame_combat_result";
		var result_ctrl = this.getFrameController(result_id);
		result_ctrl.clear();

        this.showFrame(combat_id);
    },

    closeCombat: function(data) {
        var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        if (!frame_ctrl.isCombatFinished()) {
            frame_ctrl.finishCombat();
        }
    },
    
    setCombatInfo: function(desc, characters) {
        var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setInfo(desc, characters, data_handler.character_dbref);

        this.doSetVisiblePopupSize();
    },
    
    setCombatCommands: function(commands) {
    	var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setCommands(commands);
    },
    
    setSkillResult: function(result) {
		if ("message" in result && result["message"]) {
		    var msg = text2html.parseHtml(result["message"]);
			this.displayMsg(msg);
		}
		
		var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setSkillResult(result);
    },
    
    setSkillCD: function(skill, cd, gcd) {
    	data_handler.setSkillCD(skill, cd, gcd);
    	
    	var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setSkillCD(skill, cd, gcd);
    },
    
    finishCombat: function(result) {
		var combat_id = "#frame_combat";
		var combat_ctrl = this.getFrameController(combat_id);
		combat_ctrl.finishCombat();

		var result_id = "#frame_combat_result";
		var result_ctrl = this.getFrameController(result_id);
		result_ctrl.setResult(result);

        setTimeout(this.showCombatResult, 750);
    },
    
    showCombatResult: function() {
        this.doClosePopupBox();
        this.showFrame("#frame_combat_result");
    },

    showGetExp: function(exp, combat) {
        // show exp
        this.displayMsg(LS("You got exp: ") + exp);

		if (combat) {
        	var frame_id = "#frame_combat_result";
       	 	var frame_ctrl = this.getFrameController(frame_id);
			frame_ctrl.setGetExp(exp);
		}
    },
    
    showMap: function() {
    	this.doClosePopupBox();

   		var frame_id = "#frame_map";
   		var frame = $(frame_id);
        var frame_ctrl = this.getFrameController(frame_id);

        frame.parents().show();

        //set size
        var width = frame.parent().width();
        var height = $('#middlewindow').height() * 0.8;

        frame.innerWidth(width)
        	 .innerHeight(height);

        // model dialogue
        var win_h = $(window).innerHeight();
        var dlg = $(".modal-dialog:visible:first");
        if (dlg.length > 0) {
            dlg.css("top", (win_h - dlg.height()) / 2);
        }

        frame_ctrl.showMap(map_data._current_location);
    },
    
    // close popup box
    doClosePopupBox: function() {
		$("#popup_container").hide();
    	$("#popup_container .modal-dialog").hide();
    },

    clearPromptBar: function() {
        $("#prompt_name").empty();
        $("#prompt_level").empty();
        $("#prompt_exp").empty();
        $("#prompt_hp").empty();
    },

    // set player's basic information
    setInfo: function(name, icon) {
        $("#prompt_name").text(name);

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setInfo(name, icon);
    },

    // set player's status
    setStatus: function(level, exp, max_exp, hp, max_hp, attack, defence) {
        $("#prompt_level").text(level);

        var exp_str = "--";
        if (max_exp > 0) {
            exp_str = exp + "/" + max_exp;
        }
        $("#prompt_exp").text(exp_str);

        var hp_str = hp + "/" + max_hp;
        $("#prompt_hp").text(hp_str);

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setStatus(level, exp, max_exp, hp, max_hp, attack, defence);
    },

    // set player's equipments
    setEquipments: function(equipments) {
        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setEquipments(equipments);
    },
    
    // set player's inventory
    setInventory: function(inventory) {
        var frame_ctrl = this.getFrameController("#frame_inventory");
        frame_ctrl.setInventory(inventory);
    },
    
    // set player's skills
    setSkills: function(skills) {
        var frame_ctrl = this.getFrameController("#frame_skills");
        frame_ctrl.setSkills(skills);
    },
    
    // set player's quests
    setQuests: function(quests) {
        var frame_ctrl = this.getFrameController("#frame_quests");
        frame_ctrl.setQuests(quests);
    },
    
    setScene: function(scene) {
	    var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setScene(scene);
    },
    
    showPlayerOnline: function(player) {
    	var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.addPlayer(player);
    },
    
    showPlayerOffline: function(player) {
        // If the player is looking to it, close the look window.
        var object_id = "#frame_object";
        if ($(object_id).is(":visible")) {
        	var object_ctrl = this.getFrameController(object_id);
        	var target = object_ctrl.getObject();
			if (target == player["dbref"]) {
				this.doClosePopupBox();
            }
        }

    	var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.removePlayer(player);
    },

    showObjMovedIn: function(objects) {
        var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.addObjects(objects);
    },

    showObjMovedOut: function(objects) {
        // If the player is talking to it, close the dialog window.
        var dialogue_id = "#frame_dialogue";
        if ($(dialogue_id).is(":visible")) {
        	var dialogue_ctrl = this.getFrameController(dialogue_id);
        	var target = dialogue_ctrl.getTarget();
            for (var key in objects) {
                for (var i in objects[key]) {
                    var dbref = objects[key][i]["dbref"];
                    if (target == dbref) {
                        this.doClosePopupBox();
                        break;
                    }
                }
            }
        }
        
        // If the player is looking to it, close the look window.
        var object_id = "#frame_object";
        if ($(object_id).is(":visible")) {
        	var object_ctrl = this.getFrameController(object_id);
        	var target = object_ctrl.getObject();
            for (var key in objects) {
                for (var i in objects[key]) {
                    var dbref = objects[key][i]["dbref"];
                    if (target == dbref) {
                        this.doClosePopupBox();
                        break;
                    }
                }
            }
        }

        // remove objects from scene
        var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.removeObjects(objects);
    },

    getFrameController: function(frame_id) {
        var frame = $(frame_id);
        if (frame.length > 0) {
            return frame[0].contentWindow.controller;
        }
    },

    showFrame: function(frame_id) {
        $(frame_id).parents().show();
        this.doSetVisiblePopupSize();
    },

    onLogin : function(data) {
        // show login UI
        this.clearMsgWindow();

        this.clearPromptBar();
        $("#prompt_content").show();

        this.showLoginTabs();
        this.showContent("scene");
    },
    
    onLogout : function(data) {
        // show unlogin UI
        this.clearMsgWindow();
        $("#prompt_content").hide();
        this.showUnloginTabs();
        this.showContent("login");
        
        //reconnect, show the connection screen
        Evennia.connect();
    },
    
    onPuppet: function(data) {
        data_handler.character_dbref = data["dbref"];
        data_handler.character_name = data["name"];

        this.setInfo(data["name"], data["icon"]);
    },
    
    doSetSizes: function() {
        controller.doSetWindowSize();
        controller.doSetVisiblePopupSize();
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
        var input_bar_h = 42;
        var tab_content_h = (wrapper_h - prompt_h - tab_bar_h - margin_h - input_bar_h) * 0.7;
        $('#prompt_bar').height(prompt_h);
        $('#tab_bar').height(tab_bar_h);
        $('#tab_content').height(tab_content_h);

        tab_content_h = $('#tab_content').height();
        var msg_wnd_h = wrapper_h - prompt_h - tab_bar_h - margin_h - tab_content_h - input_bar_h;
        $('#msg_wnd').height(msg_wnd_h);

        if (win_w >= 960) {
            $('#middlewindow').width(960 - 20);
        }
        else {
            $('#middlewindow').width(win_w - 20);
        }

        $("#message_input").outerWidth($('#middlewindow').width() - 118);
        
        this.doChangeVisibleFrameSize();
    },

    doSetVisiblePopupSize: function() {
        var popup_content = $("#popup_container .modal-content:visible:first");
        var frame = popup_content.find("iframe");
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
        var dlg = $(".modal-dialog:visible:first");
        if (dlg.length > 0) {
            dlg.css("top", (win_h - dlg.height()) / 2);
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
        controller.showUnloginTabs();
        controller.showContent("login");

        controller.doAutoLoginCheck();
    },
    
    onConnectionClose: function() {
        controller.showConnectTabs();
        controller.showContent("connect");

        // close popup windows
        controller.doClosePopupBox();

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
};
