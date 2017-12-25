
var controller = {

	_puppet: false,
    _solo_mode: false,
	_message_type: null,
	_waiting_begin: 0,
	
	//////////////////////////////////////////
	//
	// Message Window
	//
	//////////////////////////////////////////
	
	// clear messages in message window
	clearMsgWindow: function() {
	    $("#msg_wnd>div:not(.template)").remove();
	},

	// display a message in message window
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
    
    //////////////////////////////////////////
	//
	// Popup dialogues
	//
	//////////////////////////////////////////
	
	// popup an alert message
	showAlert: function(message) {
        this.showMessage(_("Message"), message);
	},

	// popup a normal message
	showMessage: function(header, content, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_message";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setMessage(header, content, commands);

        this.showFrame(frame_id);
	},

	// popup an object view
	showObject: function(dbref, name, icon, desc, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_object";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setObject(dbref, name, icon, desc, commands);

        this.showFrame(frame_id);
	},

	// popup dialogues
    setDialogueList: function(data) {
        if (data.length == 0) {
            if ($("#frame_dialogue").is(":visible")) {
                // close dialogue box
                this.doClosePopupBox();
            }
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

	// popup a single dialogue window
    showDialogue: function(dialogues) {
        this.doClosePopupBox();

        var frame_id = "#frame_dialogue";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setDialogues(dialogues, data_handler.getEscapes());

        this.showFrame(frame_id);
    },
    
    // popup a shop
    showShop: function(name, icon, desc, goods) {
    	this.doClosePopupBox();

        var frame_id = "#frame_shop";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setShop(name, icon, desc, goods);

        this.showFrame(frame_id);
    },
    
    // show shop window
    openShop: function() {
    	this.doClosePopupBox();
        this.showFrame("#frame_shop");
    },
    
    // popup shop goods
    showGoods: function(dbref, name, number, icon, desc, price, unit) {
		this.doClosePopupBox();

        var frame_id = "#frame_goods";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setGoods(dbref, name, number, icon, desc, price, unit);

        this.showFrame(frame_id);
    },
    
    // show get objects messages
    showGetObjects: function(accepted, rejected, combat) {
        // show accepted objects
        try {
            var first = true;
            for (var key in accepted) {
                if (first) {
                    this.displayMsg(_("You got:"));
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
                    this.displayMsg(_("You can not get:"));
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
    
    // popup a getting objects message box
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

    setCombatInfo: function(info) {
        var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setInfo(info["desc"], info["timeout"], info["characters"], data_handler.character_dbref);

        this.doSetVisiblePopupSize();
    },
    
    setCombatCommands: function(commands) {
    	var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setCommands(commands);

        this.doSetVisiblePopupSize();
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
    
    setRankings: function(rankings) {
    	var frame_id = "#frame_honours";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setRankings(rankings);
    },

    inCombatQueue: function(ave_time) {
        $("#prompt_queue").text(_("QUEUE: ") + utils.time_to_string(0));
        $("#prompt_ave_waiting").text(_("AVE: ") + utils.time_to_string(ave_time));

        this._waiting_begin = new Date().getTime();
        this._interval_id = window.setInterval("refreshWaitingTime()", 1000);
    },

    leftCombatQueue: function(ave_time) {
        if (this._interval_id != null) {
            this._interval_id = window.clearInterval(this._interval_id);
        }

        $("#prompt_queue").empty();
        $("#prompt_ave_waiting").empty();
    },

    prepareMatch: function(data) {
        var prepare_id = "#frame_confirm_combat";
		var prepare_ctrl = this.getFrameController(prepare_id);
		prepare_ctrl.setPrepareTime(data);

        controller.showFrame(prepare_id);
        var popup_content = $("#popup_confirm_combat .modal-content:visible:first");
        this.setPopupSize(popup_content);
    },
    
    prepareMatchCanceled: function(data) {
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
        controller.doClosePopupBox();
        controller.showFrame("#frame_combat_result");
    },

    showGetExp: function(exp, combat) {
        // show exp
        this.displayMsg(_("You got exp: ") + exp);

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
    
    // Set new character's information.
    showNewCharacter: function() {
        this.doClosePopupBox();
        this.showFrame("#frame_new_char");
    },

    // Delete a character.
    showDeleteCharacter: function(name, dbref) {
        this.doClosePopupBox();

        var frame_id = "#frame_delete_char";
       	var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setData(name, dbref);

        this.showFrame(frame_id);
    },
    
    // close popup box
    doClosePopupBox: function() {
		$("#popup_container").hide();
    	$("#popup_container .modal-dialog").hide();
    },

	//////////////////////////////////////////
	//
	// Prompt Bar
	//
	//////////////////////////////////////////
	
    clearPromptBar: function() {
        $("#prompt_name").empty();
        $("#prompt_level").empty();
        $("#prompt_exp").empty();
        $("#prompt_hp").empty();
        $("#prompt_queue").empty();
    },

    // set player's basic information
    setInfo: function(name, icon) {
        $("#prompt_name").text(name);

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setInfo(name, icon);
    },

    // set player's status
    setStatus: function(status) {
        $("#prompt_level").text(status["level"]["value"]);

        var exp_str = "";
        if (status["max_exp"]["value"] > 0) {
            exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
        }
        else {
            exp_str = "--/--";
        }
        $("#prompt_exp").text(exp_str);

        var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
        $("#prompt_hp").text(hp_str);

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setStatus(status);
    },
    
    // set player's all playable characters
    setAllCharacters: function(data) {
    	var frame_ctrl = this.getFrameController("#frame_select_char");
        frame_ctrl.setCharacters(data);
    },

	//////////////////////////////////////////
	//
	// Functional Windows
	//
	//////////////////////////////////////////
	
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
        data_handler.setSkills(skills);

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
        $(frame_id).show();
        $(frame_id).parents().show();
        this.doSetVisiblePopupSize();
    },

	//////////////////////////////////////////
	//
	// Events
	//
	//////////////////////////////////////////
	
	onReady: function() {
	    this.resetLanguage();
		this.showUnlogin();
    	this.showContent("login");
    	this.doSetSizes();
	},

    onConnectionOpen: function() {
    	this._puppet = false;
    	
        controller.showUnlogin();
    },
    
    onConnectionClose: function() {
    	this._puppet = false;
    	
        controller.showConnect();

        // close popup windows
        controller.doClosePopupBox();
        
        // show message
        controller.showMessage(_("Message"), _("The client connection was closed cleanly."));
    },
    
    onLogin : function(data) {
    },
    
    onPuppet : function(data) {
        data_handler.character_dbref = data["dbref"];
        data_handler.character_name = data["name"];

        this.setInfo(data["name"], data["icon"]);
    	this._puppet = true;
    
        this.showPuppet();
    },
    
    onLogout : function(data) {
    	this._puppet = false;
    	
        // show unlogin UI
        this.showUnlogin();
        
        //reconnect, show the connection screen
        Evennia.connect();
    },
    
    // connect layout
    showConnect : function() {
        this.hideTabs();
        
        $("#tab_connect").show();
        
        controller.showContent("connect");
        
        this.leftCombatQueue();

        this.clearChannels();
    },
    
    //////////////////////////////////////////
	//
	// Sizes
	//
	//////////////////////////////////////////
	
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
        var input_bar_h = 32;
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

        $("#msg_input").outerWidth($('#middlewindow').width() - 116);
        
        this.doChangeVisibleFrameSize();
    },

    doSetVisiblePopupSize: function() {
        var popup_content = $("#popup_container .modal-content:visible:first");
        this.setPopupSize(popup_content);
    },
    
    setPopupSize: function(popup_content) {
        var frame = popup_content.find("iframe");
        if (frame.length == 0) {
            return;
        }

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

    //////////////////////////////////////////
	//
	// Layouts
	//
	//////////////////////////////////////////
	
    // hide all tabs
    hideTabs : function() {
        $("#tab_pills").children().hide();
    },
        
    unselectAllTabs : function() {
        $("#tab_bar li")
            .removeClass("active")
            .removeClass("pill_active");
        $("#tab_content").children().hide();
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

    showHonours: function() {
        this.showContent("honours");
        commands.getRankings();
    },

	// puppet layout
    showPuppet : function() {
        // show login UI
        this.clearMsgWindow();

        this.clearPromptBar();
        $("#prompt_content").show();

   		// show login tabs
        this.hideTabs();

        $("#tab_scene").show();
        $("#tab_status").show();
        $("#tab_inventory").show();
        $("#tab_honours").show();
        $("#tab_system").show();

        if (!this._solo_mode) {
        	$("#tab_social").show();
        }
    
        this.showContent("scene");
    },
	
	// unlogin layout
	showUnlogin : function() {
        // show unlogin UI
        this.clearMsgWindow();
        $("#prompt_content").hide();

        this.leftCombatQueue();

    	// show unlogin tabs
        this.hideTabs();

        $("#tab_quick_login").show();
    
        this.showContent("quick_login");

        this.clearChannels();
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
    
    //////////////////////////////////////////
	//
	// Commands
	//
	//////////////////////////////////////////
	
    // send out a speech
    sendMessage: function() {
    	if (!this._puppet) {
    		return;
    	}
    	
        var message = $("#msg_input").val();
        $("#msg_input").val("");

        if (!message) {
            return;
        }

		if (this._message_type == "cmd") {
		    commands.sendRawCommand(message);
		}
		else {
	        commands.say(this._message_type, message);
	    }
    },

    //////////////////////////////////////////
	//
	// Settings
	//
	//////////////////////////////////////////

    setClient: function(settings) {
        // language
        this.setLanguage(settings["language"]);

		// game's name
        $("#game_title").text(settings["game_name"]);

        // social tab
        this._solo_mode = settings["solo_mode"];
        if (this._puppet) {
            if (this._solo_mode) {
                $("#tab_social").hide();
            }
            else {
                $("#tab_social").show();
            }
        }

        // map settings
        var map_id = "#frame_map";
        var map_ctrl = this.getFrameController(map_id);
        map_ctrl.setMap(settings["map_scale"], settings["map_room_size"]);
    },

	setLanguage: function(language) {
	    if (!local_string.setLanguage(language)) {
        	return;
        }
        
        this.resetLanguage();
		this.getFrameController("#frame_combat_result").resetLanguage();
		this.getFrameController("#frame_combat").resetLanguage();
		this.getFrameController("#frame_dialogue").resetLanguage();
		this.getFrameController("#frame_get_objects").resetLanguage();
		this.getFrameController("#frame_goods").resetLanguage();
		this.getFrameController("#frame_information").resetLanguage();
		this.getFrameController("#frame_inventory").resetLanguage();
		this.getFrameController("#frame_quick_login").resetLanguage();
		this.getFrameController("#frame_map").resetLanguage();
		this.getFrameController("#frame_message").resetLanguage();
		this.getFrameController("#frame_object").resetLanguage();
		this.getFrameController("#frame_quests").resetLanguage();
		this.getFrameController("#frame_scene").resetLanguage();
		this.getFrameController("#frame_shop").resetLanguage();
		this.getFrameController("#frame_honours").resetLanguage();
	},
	
	resetLanguage: function() {
		$("#view_level").text(_("LEVEL: "));
		$("#view_exp").text(_("EXP: "));
		$("#view_hp").text(_("HP: "));
		$("#view_connect").text(_("Connect"));
		$("#view_quick_login").text(_("Login"));
		$("#view_scene").text(_("Scene"));
		$("#view_char").text(_("Char"));
		$("#view_status").text(_("Status"));
		$("#view_inventory").text(_("Inventory"));
		$("#view_skills").text(_("Skills"));
		$("#view_quests").text(_("Quests"));
		$("#view_honours").text(_("Honours"));
		$("#view_social").text(_("Social"));
		$("#view_map").text(_("Map"));
		$("#view_system").text(_("Sys"));
		$("#view_system_char").text(_("System"));
		$("#view_logout").text(_("Logout"));
		$("#view_logout_puppet").text(_("Logout"));
		$("#msg_send").text(_("Send"));
	},
	
    clearChannels: function() {
        $("#msg_type_menu>:not(.template)").remove();
        $("#msg_select").empty();
        $("#msg_type_menu").hide();
        $("#input_bar").css("visibility", "hidden");
    },

    setChannels: function(channels) {
    	$("#msg_type_menu>:not(.template)").remove();
    	
    	var container = $("#msg_type_menu");
    	var item_template = container.find("li.template");
    	
    	var first = true;
    	for (var key in channels) {
    		var text = channels[key];
    		
    		var item = item_template.clone()
    			.removeClass("template")
    			.attr("id", "msg_type_" + key);

    		item.find("a")
    			.data("key", key)
    			.text(text);

    		item.appendTo(container);
    		
    		if (first) {
    			item.find("a")
    				.removeClass("dropdown-item")
    				.addClass("first-dropdown-item");

		    	controller._message_type = key;
    			$("#msg_select").text(text);
    			
    			first = false;
    		}
    	}
    	
    	if (first) {
    		// no channel
    		$("#input_bar").css("visibility", "hidden");
    	}
    	else {
    		$("#input_bar").css("visibility", "visible");
    	}
    },
    
    showMsgTypes: function() {
        if ($("#msg_type_menu>:not(.template)").length == 0) {
            return;
        }

    	var button = $("#msg_select");
	    var menu = $("#msg_type_menu");

	    var left = button.offset().left;
	    var top = button.offset().top - menu.outerHeight();

	    menu.show();
	    menu.offset({top: top, left: left});
    },
    
    selectMsgType: function(caller) {
    	controller._message_type = $(caller).data("key");
    	$("#msg_select").text($(caller).text());

    	$("#msg_type_menu").hide();
    },
};


function refreshWaitingTime() {
    var current_time = new Date().getTime();
    var total_time = Math.floor((current_time - controller._waiting_begin) / 1000);
    $("#prompt_queue").text(_("QUEUE: ") + utils.time_to_string(total_time));
};
