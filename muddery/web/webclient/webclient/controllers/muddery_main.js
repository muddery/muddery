

/*
 * Derive from the base class.
 */
MudderyMain = function(el) {
	BaseController.call(this, el);
	
	this.puppet = false;
    this.solo_mode = false;
	this.message_type = null;
	this.waiting_begin = 0;
	this.windows_stack = [];
}

MudderyMain.prototype = prototype(BaseController.prototype);
MudderyMain.prototype.constructor = MudderyMain;

/*
 * Document ready event.
 */
MudderyMain.prototype.init = function() {
    this.bindEvents();
}

	
/*
 * Bind events.
 */
MudderyMain.prototype.bindEvents = function() {

    // Event when client window changes
    $(window).bind("resize", this.onResize);

}


//////////////////////////////////////////
//
// Message Window
//
//////////////////////////////////////////
	
/*
 * Clear messages in message window.
 */
MudderyMain.prototype.clearMsgWindow = function() {
    $("#msg_wnd>div:not(.template)").remove();
}

/*
 * Display a message in message window.
 */
MudderyMain.prototype.displayMsg = function(msg, type) {
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
	var size = divs.length;
	if (size > max) {
		divs.slice(0, size - max).remove();
	}
	
	// scroll message window to bottom
	// $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
	// msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
}
    
//////////////////////////////////////////
//
// Popup dialogues
//
//////////////////////////////////////////

/*
 * Popup an alert message.
 */
MudderyMain.prototype.showAlert = function(message) {
    this.showMessage(mudcore.trans("Message"), message);
}

/*
 * Popup a normal message.
 */
MudderyMain.prototype.showMessage = function(header, content, commands) {
	this.doClosePopupBox();

	message_window.setMessage(header, content, commands);
    message_window.show();
}

/*
 * Popup an object view.
 */
MudderyMain.prototype.showObject = function(dbref, name, icon, desc, commands) {
	this.doClosePopupBox();

	var component = $$.component.object;
	component.setObject(dbref, name, icon, desc, commands);
	component.show();
}

/*
 * Popup dialogues.
 */
MudderyMain.prototype.setDialogueList = function(data) {
	if (data.length == 0) {
		if ($$.component.dialogue.visible()) {
			// close dialogue box
			this.doClosePopupBox();
		}
	}
	else {
		if ($$.component.combat.visible()) {
			// show dialogue after a combat
			$$.component.combat_result.setDialogue(data);
		}
		else {
			$$.data_handler.dialogues_list = data;
			dialogues = $$.data_handler.dialogues_list.shift();
			this.showDialogue(dialogues);
		}
	}
}

/*
 * Popup a single dialogue window.
 */
MudderyMain.prototype.showDialogue = function(dialogues) {
	this.doClosePopupBox();

    var component = $$.component.dialogue;
	component.setDialogues(dialogues, $$.data_handler.getEscapes());
	component.show();
}
  
/*  
 * Popup a shop.
 */
MudderyMain.prototype.showShop = function(name, icon, desc, goods) {
	this.doClosePopupBox();

	var component = $$.component.shop;
	component.setShop(name, icon, desc, goods);
	component.show();
}
  
/*  
 * Show shop window.
 */
MudderyMain.prototype.openShop = function() {
	this.doClosePopupBox();
	$$.component.shop.show();
}
  
/*  
 * Popup shop goods.
 */
MudderyMain.prototype.showGoods = function(dbref, name, number, icon, desc, price, unit) {
	this.doClosePopupBox();

	var component = $$.component.goods;
	component.setGoods(dbref, name, number, icon, desc, price, unit);
	component.show()
}
  
/*  
 * Show get objects messages.
 */
MudderyMain.prototype.showGetObjects = function(accepted, rejected, combat) {
	// show accepted objects
	try {
		var first = true;
		for (var key in accepted) {
			if (first) {
				this.displayMsg(mudcore.trans("You got:"));
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
				this.displayMsg(mudcore.trans("You can not get:"));
				first = false;
			}
			this.displayMsg(key + ": " + rejected[key]);
		}
	}
	catch(error) {
		console.error(error.message);
	}

	if (combat) {
		$$.component.combat_result.setGetObjects(accepted, rejected);
	}
	else {
		// If not in combat.
		var popup_box = $('#popup_box');
		if (popup_box.length == 0) {
			// If there is no other boxes, show getting object box.
			this.popupGetObjects(accepted, rejected);
		}
	}
}
  
/*  
 * popup a getting objects message box
 */
MudderyMain.prototype.popupGetObjects = function(accepted, rejected) {
	this.doClosePopupBox();

	var component = $$.component.get_objects;
	component.setObjects(accepted, rejected);
	component.show();
}
   
/*
 * Show the combat window. 
 */
MudderyMain.prototype.showCombat = function(combat) {     
	this.doClosePopupBox();
	
	$$.component.combat_result.clear();
	
	var component = $$.component.combat;
	component.reset($$.data_handler.skill_cd_time);
	component.show();
}

/*
 * Close the combat window.
 */
MudderyMain.prototype.closeCombat = function(data) {
	var component = $$.component.combat;
	if (!component.isCombatFinished()) {
		component.finishCombat();
	}
}
    
/*
 * Set combat data.
 */
MudderyMain.prototype.setCombatInfo = function(info) {
	$$.component.combat.setInfo(info["desc"], info["timeout"], info["characters"], $$.data_handler.character_dbref);
}
    
/*
 * Set commands used in the combat.
 */
MudderyMain.prototype.setCombatCommands = function(commands) {
	var component = $$.component.combat;
	component.setCommands(commands);
	component.show();
}
    
/*
 * Cast a combat skill.
 */
MudderyMain.prototype.setSkillCast = function(result) {
    if ("status" in result && $$.data_handler.character_dbref in result["status"]) {
        this.setCombatStatus(result["status"][$$.data_handler.character_dbref])
    }
    
    var component = $$.component.combat;
	if (component.isCombatFinished()) {
	    var message = "";
		if ("cast" in result && result["cast"]) {
			message += mudcore.text2html.parseHtml(result["cast"]) + " ";
		}
		if ("result" in result && result["result"]) {
			message += mudcore.text2html.parseHtml(result["result"]);
		}
		if (message) {
			this.displayMsg(message);
		}
	}
	else {
		component.setSkillCast(result);
	}
}

/*
 * Set skill's cd.
 */
MudderyMain.prototype.setSkillCD = function(skill, cd, gcd) {
	$$.data_handler.setSkillCD(skill, cd, gcd);
	
	$$.component.combat.setSkillCD(skill, cd, gcd);
}
    
/*
 * Set the rankings of player honours.
 */
MudderyMain.prototype.setRankings = function(rankings) {
	$$.component.honours.setRankings(rankings);
}

/*
 * Player in honour combat queue.
 */
MudderyMain.prototype.inCombatQueue = function(ave_time) {
	$("#prompt_queue").text(mudcore.trans("QUEUE: ") + $$.utils.time_to_string(0));
	this.displayMsg(mudcore.trans("You are in queue now. Average waiting time is ") + $$.utils.time_to_string(ave_time) + mudcore.trans("."));

	this.waiting_begin = new Date().getTime();
	this.interval_id = window.setInterval("refreshWaitingTime()", 1000);
}

/*
 * The player has prepared the honour match.
 */
MudderyMain.prototype.prepareMatch = function(data) {
	var component = $$.component.confirm_combat;
	component.init(data);
	component.show();
}

/*
 * The player has rejected the honour match.
 */
MudderyMain.prototype.matchRejected = function(character_id) {
	$$.component.confirm_combat.closeBox();

	if ("#" + character_id == $$.data_handler.character_dbref) {
		this.displayMsg(mudcore.trans("You have rejected the combat."));
	}
	else {
		this.displayMsg(mudcore.trans("Your opponent has rejected the combat."));
	}
}

/*
 * Close the prepare match box.
 */
MudderyMain.prototype.closePrepareMatchBox = function() {
	$("#popup_confirm_combat").hide();
	$("#frame_confirm_combat").hide();
}

/*
 * The combat has finished.
 */
MudderyMain.prototype.finishCombat = function(result) {
	$$.component.combat.finishCombat();
	$$.component.combat_result.setResult(result);

	setTimeout(this.showCombatResult, 750);
}
    
/*
 * Set the combat's result.
 */
MudderyMain.prototype.showCombatResult = function() {
	window_main.doClosePopupBox();
	$$.component.combat_result.show();
}

/*
 * Set the exp the player get.
 */
MudderyMain.prototype.showGetExp = function(exp, combat) {
	// show exp
	this.displayMsg(mudcore.trans("You got exp: ") + exp);

	if (combat) {
	    $$.component.combat_result.setGetExp(exp);
	}
}
    
/*
 * Display the map.
 */
MudderyMain.prototype.showMap = function() {
	this.doClosePopupBox();
	
	var component = $$.component.map;
    component.show();
	component.showMap($$.map_data._current_location);
}

/*
 *  Delete a character.
 */
MudderyMain.prototype.showDeleteCharacter = function(name, dbref) {
	this.doClosePopupBox();

	var component = $$.component.delete_char;
	component.setData(name, dbref);
	component.show();
}

/*
 *  Close the popup box.
 */
MudderyMain.prototype.doClosePopupBox = function() {
	$("#popup_container").hide();
	$("#popup_container .modal-dialog").hide();
}

//////////////////////////////////////////
//
// Prompt Bar
//
//////////////////////////////////////////
MudderyMain.prototype.setPromptBar = function() {
    this.clearPromptBar();

    var template = $("#prompt_content>.template");

    var item = this.cloneTemplate(template);
    item.attr("id", "prompt_name");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_level");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_exp");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_hp");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_queue");
}

/*
 * Clear the prompt bar.
 */
MudderyMain.prototype.clearPromptBar = function() {
	this.clearElements("#prompt_content");
}

/* 
 * Set the player's basic information.
 */
MudderyMain.prototype.setInfo = function(name, icon) {
	$("#prompt_name").text(name);
	
	$$.component.information.setInfo(name, icon);
}

/*
 *  Set the player's status.
 */
MudderyMain.prototype.setStatus = function(status) {
	$$.data_handler.character_level = status["level"]["value"];
	$("#prompt_level").text(mudcore.trans("LEVEL: ") + status["level"]["value"]);

    if ("exp" in status && "max_exp" in status) {
        var exp_str = "";
        if (status["max_exp"]["value"] > 0) {
            exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
        }
        else {
            exp_str = "--/--";
        }
        $("#prompt_exp").text(mudcore.trans("EXP: ") + exp_str);
    }

    if ("hp" in status && "max_hp" in status) {
        var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
        $("#prompt_hp").text(mudcore.trans("HP: ") + hp_str);
    }
    
	$$.component.information.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
MudderyMain.prototype.setCombatStatus = function(status) {
	var hp_str = status["hp"] + "/" + status["max_hp"];
	$("#prompt_hp").text(mudcore.trans("HP: ") + hp_str);

	$$.component.information.setCombatStatus(status);
}

//////////////////////////////////////////
//
// Functional Windows
//
//////////////////////////////////////////

/* 
 * Set the player's equipments.
 */
MudderyMain.prototype.setEquipments = function(equipments) {
	$$.component.information.setEquipments(equipments);
}
    
/*
 * Set the player's inventory.
 */
MudderyMain.prototype.setInventory = function(inventory) {
	$$.component.inventory.setInventory(inventory);
}

/*
 * Set the player's skills.
 */
MudderyMain.prototype.setSkills = function(skills) {
	$$.data_handler.setSkills(skills);

	$$.component.skills.setSkills(skills);
}

/* 
 * Set the player's quests.
 */
MudderyMain.prototype.setQuests = function(quests) {
	$$.component.quests.setQuests(quests);
}

/*
 * Set the player's current scene.
 */
MudderyMain.prototype.setScene = function(scene) {
	$$.component.scene.setScene(scene);
}
    
/*
 * Notify a player has been online.
 */
MudderyMain.prototype.showPlayerOnline = function(player) {
	$$.component.scene.addPlayer(player);
}
    
/*
 * Notify a player has been offline.
 */
MudderyMain.prototype.showPlayerOffline = function(player) {
	// If the player is looking to it, close the look window.
	var component = $$.component.object;
	if (component.visible()) {
		component.onObjMovedOut(player["dbref"]);
	}

	$$.component.scene.removePlayer(player);
}

/*
 * Notify an object has moved to the player's current place.
 */
MudderyMain.prototype.showObjMovedIn = function(objects) {
	$$.component.scene.addObjects(objects);
}

/*
 * Notify an object has moved out the player's current place.
 */
MudderyMain.prototype.showObjMovedOut = function(objects) {
	// If the player is talking to it, close the dialog window.
	var dialogue = $$.component.dialogue;
	if (dialogue.visible()) {
		dialogue.onObjsMovedOut(objects);
	}
        
	// If the player is looking to it, close the look window.
	var object = $$.component.object;
	if (object.visible()) {
		object.onObjsMovedOut(objects);
	}

	// remove objects from scene
	$$.component.scene.removeObjects(objects);
}


//////////////////////////////////////////
//
// Events
//
//////////////////////////////////////////

/*
 * Event when the connection opens.
 */
MudderyMain.prototype.onConnectionOpen = function() {
    var self = main_window;
    
	self.puppet = false;

	self.showLoginWindow();
	login_window.checkAutoLogin();
}

/*
 * Event when the connection closes.
 */
MudderyMain.prototype.onConnectionClose = function() {
    var self = main_window;

	self.puppet = false;

	self.showLoginWindow();

	// close popup windows
	self.doClosePopupBox();
	
	// show message
	self.showMessage(mudcore.trans("Message"), mudcore.trans("The client connection was closed cleanly."));
}
    
/*
 * Event when the player logins.
 */
MudderyMain.prototype.onLogin = function(data) {
    login_window.onLogin();
	this.showSelectChar();
}
    
/*
 * Event when the player logs out.
 */
MudderyMain.prototype.onLogout = function(data) {
	this.puppet = false;
	
	// show unlogin UI
	this.showLoginWindow();
	
	//reconnect, show the connection screen
	Evennia.connect();
}

/*
 * Event when the player created a new character.
 */
MudderyMain.prototype.onCharacterCreated = function(data) {
	// close popup windows
	window_main.doClosePopupBox();
}

/*
 * Event when the player deleted a character.
 */
MudderyMain.prototype.onCharacterDeleted = function(data) {
	// close popup windows
	window_main.doClosePopupBox();
}

/*
 * Event when the player puppets a character.
 */
MudderyMain.prototype.onPuppet = function(data) {
	$$.data_handler.character_dbref = data["dbref"];
	$$.data_handler.character_name = data["name"];

	this.showPuppet();
	this.setInfo(data["name"], data["icon"]);

	this.puppet = true;
}

/*
 * Event when the player unpuppets a character.
 */
MudderyMain.prototype.onUnpuppet = function(data) {
	this.puppet = false;
	this.showSelectChar();
}
    
//////////////////////////////////////////
//
// Sizes
//
//////////////////////////////////////////

/*
/*
 * Reset all sizes.
 */
MudderyMain.prototype.onResize = function() {
}

//////////////////////////////////////////
//
// Layouts
//
//////////////////////////////////////////

MudderyMain.prototype.hideAllWindows = function() {
    $(".popup-window").hide();
    $(".main-window").hide();
}

/*
 * Hide all tabs.
 */
MudderyMain.prototype.hideTabs = function() {
    $("#tab_pills").children().hide();
}

/*
 * Unselect all tabs.
 */
MudderyMain.prototype.unselectAllTabs = function() {
	$("#tab_bar li")
		.removeClass("active")
		.removeClass("pill_active");
	$("#tab_content").children().hide();
}

/* 
 * Hide all tab contents.    
 */
MudderyMain.prototype.hideAllContents = function() {
	$("#tab_bar li")
		.removeClass("active")
		.removeClass("pill_active");

	$("#tab_content").children().hide();
}

/*
 * Show a tab's content.
 */
MudderyMain.prototype.showContent = function(frame_name) {
	this.hideAllContents();
	
	$("#tab_" + frame_name)
		.addClass("active")
		.addClass("pill_active");

    var controller = $$.component[frame_name];
    if (controller) {
        controller.show();
    }
}

/*
 * Show honour tab's content.
 */
MudderyMain.prototype.showHonours = function() {
	this.showContent("honours");
	mudcore.service.getRankings();
}

/*
 * Show the layout when players puppet.
 */
MudderyMain.prototype.showPuppet = function() {
	// show login UI
	this.clearMsgWindow();

	this.setPromptBar();

	// show login tabs
	this.hideTabs();

	$("#tab_scene").show();
	$("#tab_character").show();
	$("#tab_honours").show();
	$("#tab_map").show();
	$("#tab_system").show();

	if (!this.solo_mode) {
		$("#tab_social").show();
	}

	this.showContent("scene");
}


/*
 * Set the windows stack to a new window.
 */
MudderyMain.prototype.gotoWindow = function(win_controller) {
	this.clearMsgWindow();
	this.clearPromptBar();

	// show unlogin tabs
	this.hideAllWindows();
	win_controller.reset();
	win_controller.show();
	this.windows_stack = [win_controller];

	this.clearChannels();
}


/*
 * Push a new window to the windows stack.
 */
MudderyMain.prototype.pushWindow = function(win_controller) {
	this.clearMsgWindow();
	this.clearPromptBar();

	// show unlogin tabs
	this.hideAllWindows();
	win_controller.reset();
	win_controller.show();
	this.windows_stack.push(win_controller);

	this.clearChannels();
}


/*
 * Pop a window from the windows stack.
 */
MudderyMain.prototype.popWindow = function() {
    if (this.windows_stack.length == 0) {
        return;
    }

	this.clearMsgWindow();
	this.clearPromptBar();

	// show unlogin tabs
	this.hideAllWindows();
	this.windows_stack.pop();
	var win_controller = this.windows_stack[this.windows_stack.length - 1];
	win_controller.show();

	this.clearChannels();
}


/*
 * Show the layout when players unlogin.
 */
MudderyMain.prototype.showLoginWindow = function() {
	// show unlogin UI
	this.gotoWindow(login_window);
}
    
/*
 * Show the layout when players logged in and going to select a character.
 */
MudderyMain.prototype.showSelectChar = function() {
	this.gotoWindow(select_char_window);
}


/*
 * Show the layout when players has not connected.
 */
MudderyMain.prototype.showConnect = function() {
	this.hideTabs();
	
	$("#tab_connect").show();
	
	window_main.showContent("connect");
	
	this.clearChannels();
}

//////////////////////////////////////////
//
// Commands
//
//////////////////////////////////////////

/*
 * Command to send out a speech.
 */
MudderyMain.prototype.sendMessage = function() {
	if (!this.puppet) {
		return;
	}
	
	var message = $("#bar_msg_input").val();
	$("#bar_msg_input").val("");

	if (!message) {
		return;
	}

	if (this.message_type == "cmd") {
		mudcore.service.sendRawCommand(message);
	}
	else {
		mudcore.service.say(this.message_type, message);
	}
}

//////////////////////////////////////////
//
// Settings
//
//////////////////////////////////////////

/*
 * Set the client.
 */
MudderyMain.prototype.setClient = function(settings) {
	// game's name
	$("#game_title").text(settings["game_name"]);

	// social tab
	this.solo_mode = settings["solo_mode"];
	if (this.puppet) {
		if (this.solo_mode) {
			$("#tab_social").hide();
		}
		else {
			$("#tab_social").show();
		}
	}

	// honour settings
	//$$.component.honours.setMinHonourLevel(settings["min_honour_level"]);

	// map settings
	//$$.component.map.setMap(settings["map_scale"], settings["map_room_size"], settings["map_room_box"]);
}

/*
 *  Set the player's all playable characters.
 */
MudderyMain.prototype.setAllCharacters = function(data) {
	select_char_window.setCharacters(data);
}
	
/* 
 * Clear all channels' messages.
 */
MudderyMain.prototype.clearChannels = function() {
	$("#bar_msg_type_menu>:not(.template)").remove();
	$("#bar_msg_select").empty();
	$("#bar_msg_type_menu").hide();
	$("#input_bar").css("visibility", "hidden");
}

/*
 * Set available channels.
 */
MudderyMain.prototype.setChannels = function(channels) {
	$("#bar_msg_type_menu>:not(.template)").remove();
	
	var container = $("#bar_msg_type_menu");
	var item_template = container.find("li.template");
	
	var first = true;
	for (var key in channels) {
		var text = channels[key];
		
		var item = item_template.clone()
			.removeClass("template")
			.attr("id", "bar_msg_type_" + key);

		item.find("a")
			.data("key", key)
			.text(text);

		item.appendTo(container);
		
		if (first) {
			item.find("a")
				.removeClass("dropdown-item")
				.addClass("first-dropdown-item");

			window_main.message_type = key;
			$("#bar_msg_select").text(text);
			
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
}

/*
 * Set available message types.
 */
MudderyMain.prototype.showMsgTypes = function() {
	if ($("#bar_msg_type_menu>:not(.template)").length == 0) {
		return;
	}

	var button = $("#bar_msg_select");
	var menu = $("#bar_msg_type_menu");

	var left = button.offset().left;
	var top = button.offset().top - menu.outerHeight();

	menu.show();
	menu.offset({top: top, left: left});
}

/*
 * Event when select a message type.
 */
MudderyMain.prototype.selectMsgType = function(caller) {
	window_main.message_type = $(caller).data("key");
	var text = $(caller).text();
	$("#bar_msg_select").text($(caller).text());

	$("#bar_msg_type_menu").hide();
}


/******************************************
 *
 * Popup message window.
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyMessage = function(el) {
	BasePopupController.call(this, el);
}

MudderyMessage.prototype = prototype(BasePopupController.prototype);
MudderyMessage.prototype.constructor = MudderyMessage;

/*
 * Bind events.
 */
MudderyMessage.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
	this.onClick(".msg-footer", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyMessage.prototype.onClose = function(element) {
    this.el.hide();
    this.select(".msg-header-text").empty();
	this.select(".msg-body").empty();
	this.select(".msg-footer").empty();
}

/*
 * Event when clicks a command button.
 */
MudderyMessage.prototype.onCommand = function(element) {
	this.onClose();

	var cmd = this.select(element).data("cmd_name");
	var args = this.select(element).data("cmd_args");
	if (cmd) {
		mudcore.service.sendCommandLink(cmd, args);
	}
}

/*
 * Set message's data.
 */
MudderyMessage.prototype.setMessage = function(header, content, commands) {
    var header = mudcore.text2html.parseHtml(header) || "&nbsp;";
	this.select(".msg-header-text").html(header);
	this.select(".msg-body").html(mudcore.text2html.parseHtml(content));

	if (!commands) {
		commands = [{"name": mudcore.trans("OK"),
					 "cmd": "",
					 "args": ""}];
	}
	this.addButtons(commands);
}

/*
 * Set command buttons.
 */
MudderyMessage.prototype.addButtons = function(commands) {
    var container = this.select(".msg-footer");
	for (var i in commands) {
		var button = commands[i];
		var name = mudcore.text2html.parseHtml(button["name"]);

		$("<button>").attr("type", "button")
		    .addClass("msg-button")
		    .data("cmd_name", button["cmd"])
			.data("cmd_args", button["args"])
			.html(name)
			.appendTo(container);
	}
}


/******************************************
 *
 * Login Window
 *
 ******************************************/
 
/*
 * Derive from the base class.
 */
MudderyLogin = function(el) {
	BaseController.call(this, el);
}

MudderyLogin.prototype = prototype(BaseController.prototype);
MudderyLogin.prototype.constructor = MudderyLogin;

/*
 * Bind events.
 */
MudderyLogin.prototype.bindEvents = function() {
    this.onClick(".button-tab-login", this.onTabLogin);
    this.onClick(".button-tab-register", this.onTabRegister);
    this.onClick(".button-login", this.onClickLogin);
	this.onClick(".button-register", this.onClickRegister);
    this.on(".checkbox-auto-login", "change", this.onAutoLogin);
}

/*
 * Event when clicks the login tab.
 */
MudderyLogin.prototype.onTabLogin = function(element) {
    if (this.select(".button-tab-login").hasClass("tab-activate")) {
        return;
    }
    
    this.select(".button-tab-login").removeClass("tab-inactivate");
    this.select(".button-tab-login").addClass("tab-activate");
    
    this.select(".button-tab-register").removeClass("tab-activate");
    this.select(".button-tab-register").addClass("tab-inactivate");
    
    this.select(".login-form").show();
    this.select(".register-form").hide();
}

/*
 * Event when clicks the register tab.
 */
MudderyLogin.prototype.onTabRegister = function(element) {
    if (this.select(".button-tab-register").hasClass("tab-activate")) {
        return;
    }
    
    this.select(".button-tab-login").removeClass("tab-activate");
    this.select(".button-tab-login").addClass("tab-inactivate");
    
    this.select(".button-tab-register").removeClass("tab-inactivate");
    this.select(".button-tab-register").addClass("tab-activate");
    
    this.select(".login-form").hide();
    this.select(".register-form").show();
}

/*
 * Event when clicks the register button.
 */
MudderyLogin.prototype.onClickRegister = function(element) {
    var playername = this.select(".reg-name").val();
    var password = this.select(".reg-password").val();
    var password_verify = this.select(".reg-password-verify").val();

    mudcore.service.register(playername, password, password_verify, true);
    this.clearValues();
}

/*
 * Event on click the login button.
 */
MudderyLogin.prototype.onClickLogin = function(element) {
    var name = this.select(".login-name").val();
    var password = this.select(".login-password").val();
    mudcore.service.login(name, password);
}

/*
 * Event on click the auto login checkbox.
 */
MudderyLogin.prototype.onAutoLogin = function(element) {
    var auto_login = this.select(".checkbox-auto-login").prop("checked");

    if (!auto_login) {
        mudcore.service.doRemoveAutoLogin();
    }
}

/*
 * Clear user inputted values.
 */
MudderyLogin.prototype.clearValues = function() {
    this.select(".login-name").val("");
    this.select(".login-password").val("");
    this.select(".reg-name").val("");
    this.select(".reg-password").val("");
    this.select(".reg-password-verify").val("");
    this.select(".checkbox-auto-login").prop("checked", false);
}

/*
 * Set values.
 */
MudderyLogin.prototype.setValues = function(playername, password, auto_login) {
    this.select(".login-name").val(playername);
    this.select(".login-password").val(password);
    this.select(".checkbox-auto-login").prop("checked", auto_login);
}

/*
 * Remove auto login.
 */
MudderyLogin.prototype.removeAutoLogin = function() {
    localStorage.login_name = "";
    localStorage.login_password = "";
    localStorage.is_auto_login = "";
}

/*
 * Check the auto login setting and do auto login.
 */
MudderyLogin.prototype.checkAutoLogin = function() {
    if (localStorage.is_auto_login) {
        var playername = localStorage.login_name;
        var password = localStorage.login_password;

        login_window.setValues(playername, password, true);
	    mudcore.service.login(playername, playerpassword);
    }
}

/*
 * On user login.
 */
MudderyLogin.prototype.onLogin = function() {
    var auto_login = this.select(".checkbox-auto-login").prop("checked");

    if (auto_login) {
        var name = this.select(".login-name").val();
        var password = this.select(".login-password").val();

        // Save the name and password.
        localStorage.login_name = playername;
        localStorage.login_password = password;
        localStorage.is_auto_login = "1";
    }
}


/******************************************
 *
 * Select Character Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderySelectChar = function(el) {
	BaseTabController.call(this, el);
}

MudderySelectChar.prototype = prototype(BaseTabController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick(".button-back", this.onClickBack);
    this.onClick(".button-new-char", this.onNewCharacter);
    this.onClick("#character_items", ".char_name", this.onSelectCharacter);
    this.onClick("#character_items", ".button_delete", this.onDeleteCharacter);
}

/*
 * Event when clicks the back button.
 */
MudderySelectChar.prototype.onClickBack = function(element) {
    mudcore.service.logout();
    Evennia.reconnect();
    main_window.showLoginWindow();
}

/*
 * Event when clicks the new character button.
 */
MudderySelectChar.prototype.onNewCharacter = function(element) {
    main_window.pushWindow(new_char_window);
}

/*
 * On select a character.
 */
MudderySelectChar.prototype.onSelectCharacter = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.puppetCharacter(dbref);
}

/*
 * On delete a character.
 */
MudderySelectChar.prototype.onDeleteCharacter = function(element) {
	var name = this.select(element).data("name");
	var dbref = this.select(element).data("dbref");
	$$.main.showDeleteCharacter(name, dbref);
}

/*
 * Set playable characters.
 */
MudderySelectChar.prototype.setCharacters = function(characters) {
    this.clearElements("#character_items");
	var template = this.select("#character_items>.template");

	for (var i in characters) {
		var obj = characters[i];
		var item = this.cloneTemplate(template);

		item.find(".char_name")
			.data("dbref", obj["dbref"])
			.text(obj["name"]);

		item.find(".button_delete")
			.data("name", obj["name"])
			.data("dbref", obj["dbref"]);
	}
}


/******************************************
 *
 * New Character Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyNewChar = function(el) {
	BaseTabController.call(this, el);
}

MudderyNewChar.prototype = prototype(BaseTabController.prototype);
MudderyNewChar.prototype.constructor = MudderyNewChar;

/*
 * Bind events.
 */
MudderyNewChar.prototype.bindEvents = function() {
    this.onClick(".button-back", this.onClickBack);
    this.onClick(".button-create", this.onCreate);
}

/*
 * Event when clicks the back button.
 */
MudderyNewChar.prototype.onClickBack = function(element) {
    main_window.popWindow();
}

/*
 * Event when clicks the create button.
 */
MudderyNewChar.prototype.onCreate = function(element) {
	var char_name = this.select(".new-char-name").val();
	mudcore.service.createCharacter(char_name);
	this.reset();
}

/*
 * Reset the element.
 */
MudderyNewChar.prototype.reset = function() {
    this.select(".new-char-name").val("");
}
