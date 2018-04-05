//@ sourceURL=/controller/muddery_main.js

if (typeof(require) != "undefined") {
    require("../css/webclient.css");
    require("../css/main.css");

    require("muddery_login.js")
}

/*
 * Derive from the base class.
 */
function MudderyMain() {
	BaseController.call(this);
	
	this.puppet = false;
    this.solo_mode = false;
	this.message_type = null;
	this.waiting_begin = 0;
}

MudderyMain.prototype = prototype(BaseController.prototype);
MudderyMain.prototype.constructor = MudderyMain;

/*
 * Document ready event.
 */
MudderyMain.prototype.onReady = function() {
    this.resetLanguage();
    this.bindEvents();

	this.showUnlogin();
    this.showContent("login");
    this.doSetSizes();
}
	
/*
 * Reset the view's language.
 */
MudderyMain.prototype.resetLanguage = function() {
	$("#view_connect").text($$("Connect"));
	$("#view_login").text($$("Login"));
	$("#view_register").text($$("Register"));
	$("#view_password").text($$("Password"));
	$("#view_select_char").text($$("Select Char"));
	$("#view_scene").text($$("Scene"));
	$("#view_char").text($$("Char"));
	$("#view_status").text($$("Status"));
	$("#view_inventory").text($$("Inventory"));
	$("#view_skills").text($$("Skills"));
	$("#view_quests").text($$("Quests"));
	$("#view_social").text($$("Social"));
	$("#view_honours").text($$("Honours"));
	$("#view_map").text($$("Map"));
	$("#view_system").text($$("Sys"));
	$("#view_system_char").text($$("System"));
	$("#view_logout").text($$("Logout"));
	$("#view_logout_puppet").text($$("Logout"));
	$("#view_password_puppet").text($$("Password"));
	$("#view_unpuppet").text($$("Unpuppet"));
	$("#msg_send").text($$("Send"));
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
	msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
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
    this.showMessage($$("Message"), message);
}

/*
 * Popup a normal message.
 */
MudderyMain.prototype.showMessage = function(header, content, commands) {
	this.doClosePopupBox();

	var frame_id = "#frame_message";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setMessage(header, content, commands);

	this.showFrame(frame_id);
}

/*
 * Popup an object view.
 */
MudderyMain.prototype.showObject = function(dbref, name, icon, desc, commands) {
	this.doClosePopupBox();

	var frame_id = "#frame_object";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setObject(dbref, name, icon, desc, commands);

	this.showFrame(frame_id);
}

/*
 * Popup dialogues.
 */
MudderyMain.prototype.setDialogueList = function(data) {
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
}

/*
 * Popup a single dialogue window.
 */
MudderyMain.prototype.showDialogue = function(dialogues) {
	this.doClosePopupBox();

	var frame_id = "#frame_dialogue";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setDialogues(dialogues, data_handler.getEscapes());

	this.showFrame(frame_id);
}
  
/*  
 * Popup a shop.
 */
MudderyMain.prototype.showShop = function(name, icon, desc, goods) {
	this.doClosePopupBox();

	var frame_id = "#frame_shop";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setShop(name, icon, desc, goods);

	this.showFrame(frame_id);
}
  
/*  
 * Show shop window.
 */
MudderyMain.prototype.openShop = function() {
	this.doClosePopupBox();
	this.showFrame("#frame_shop");
}
  
/*  
 * Popup shop goods.
 */
MudderyMain.prototype.showGoods = function(dbref, name, number, icon, desc, price, unit) {
	this.doClosePopupBox();

	var frame_id = "#frame_goods";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setGoods(dbref, name, number, icon, desc, price, unit);

	this.showFrame(frame_id);
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
				this.displayMsg($$("You got:"));
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
				this.displayMsg($$("You can not get:"));
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
}
  
/*  
 * popup a getting objects message box
 */
MudderyMain.prototype.popupGetObjects = function(accepted, rejected) {
	this.doClosePopupBox();

	var frame_id = "#frame_get_objects";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setObjects(accepted, rejected);

	this.showFrame(frame_id);
}
   
/*
 * Show the combat window. 
 */
MudderyMain.prototype.showCombat = function(combat) {     
	this.doClosePopupBox();

	var combat_id = "#frame_combat";
	var combat_ctrl = this.getFrameController(combat_id);
	combat_ctrl.reset(data_handler.skill_cd_time);
	
	var result_id = "#frame_combat_result";
	var result_ctrl = this.getFrameController(result_id);
	result_ctrl.clear();

	this.showFrame(combat_id);
}

/*
 * Close the combat window.
 */
MudderyMain.prototype.closeCombat = function(data) {
	var frame_id = "#frame_combat";
	var frame_ctrl = this.getFrameController(frame_id);
	if (!frame_ctrl.isCombatFinished()) {
		frame_ctrl.finishCombat();
	}
}
    
/*
 * Set combat data.
 */
MudderyMain.prototype.setCombatInfo = function(info) {
	var frame_id = "#frame_combat";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setInfo(info["desc"], info["timeout"], info["characters"], data_handler.character_dbref);

	this.doSetVisiblePopupSize();
}
    
/*
 * Set commands used in the combat.
 */
MudderyMain.prototype.setCombatCommands = function(commands) {
	var frame_id = "#frame_combat";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setCommands(commands);

	this.doSetVisiblePopupSize();
}
    
/*
 * Cast a combat skill.
 */
MudderyMain.prototype.setSkillCast = function(result) {
    if ("status" in result && data_handler.character_dbref in result["status"]) {
        this.setCombatStatus(result["status"][data_handler.character_dbref])
    }
    
	var frame_id = "#frame_combat";
	var frame_ctrl = this.getFrameController(frame_id);
	if (frame_ctrl.isCombatFinished()) {
	    var message = "";
		if ("cast" in result && result["cast"]) {
			message += text2html.parseHtml(result["cast"]) + " ";
		}
		if ("result" in result && result["result"]) {
			message += text2html.parseHtml(result["result"]);
		}
		if (message) {
			this.displayMsg(message);
		}
	}
	else {
		frame_ctrl.setSkillCast(result);
	}
}

/*
 * Set skill's cd.
 */
MudderyMain.prototype.setSkillCD = function(skill, cd, gcd) {
	data_handler.setSkillCD(skill, cd, gcd);
	
	var frame_id = "#frame_combat";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setSkillCD(skill, cd, gcd);
}
    
/*
 * Set the rankings of player honours.
 */
MudderyMain.prototype.setRankings = function(rankings) {
	var frame_id = "#frame_honours";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setRankings(rankings);
}

/*
 * Player in honour combat queue.
 */
MudderyMain.prototype.inCombatQueue = function(ave_time) {
	$("#prompt_queue").text($$("QUEUE: ") + utils.time_to_string(0));
	this.displayMsg($$("You are in queue now. Average waiting time is ") + utils.time_to_string(ave_time) + $$("."));

	this.waiting_begin = new Date().getTime();
	this.interval_id = window.setInterval("refreshWaitingTime()", 1000);
}

/*
 * Player left the honour combat queue.
 */
MudderyMain.prototype.leftCombatQueue = function(ave_time) {
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}

	$("#prompt_queue").empty();

	var frame_id = "#frame_honours";
	var frame_ctrl = this.getFrameController(frame_id);
	if (frame_ctrl) {
		frame_ctrl.quitCombatQueue();
	}
	
	var prepare_id = "#frame_confirm_combat";
	var prepare_ctrl = this.getFrameController(prepare_id);
	if (prepare_ctrl) {
		prepare_ctrl.closeBox();
	}
}

/*
 * The player has prepared the honour match.
 */
MudderyMain.prototype.prepareMatch = function(data) {
	var prepare_id = "#frame_confirm_combat";
	var prepare_ctrl = this.getFrameController(prepare_id);
	prepare_ctrl.setTime(data);

	this.showFrame(prepare_id);
	var popup_dialog = $("#popup_confirm_combat .modal-dialog:visible:first");
	this.setPopupSize(popup_dialog);
}

/*
 * The player has rejected the honour match.
 */
MudderyMain.prototype.matchRejected = function(character_id) {
	var prepare_id = "#frame_confirm_combat";
	var prepare_ctrl = this.getFrameController(prepare_id);
	prepare_ctrl.closeBox();

	if ("#" + character_id == data_handler.character_dbref) {
		this.displayMsg($$("You have rejected the combat."));
	}
	else {
		this.displayMsg($$("Your opponent has rejected the combat."));
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
	var combat_id = "#frame_combat";
	var combat_ctrl = this.getFrameController(combat_id);
	combat_ctrl.finishCombat();

	var result_id = "#frame_combat_result";
	var result_ctrl = this.getFrameController(result_id);
	result_ctrl.setResult(result);

	setTimeout(this.showCombatResult, 750);
}
    
/*
 * Set the combat's result.
 */
MudderyMain.prototype.showCombatResult = function() {
	controller.doClosePopupBox();
	controller.showFrame("#frame_combat_result");
}

/*
 * Set the exp the player get.
 */
MudderyMain.prototype.showGetExp = function(exp, combat) {
	// show exp
	this.displayMsg($$("You got exp: ") + exp);

	if (combat) {
		var frame_id = "#frame_combat_result";
		var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setGetExp(exp);
	}
}
    
/*
 * Display the map.
 */
MudderyMain.prototype.showMap = function() {
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
}

/*
 *  Set new character's information.
 */
MudderyMain.prototype.showNewCharacter = function() {
	this.doClosePopupBox();
	this.showFrame("#frame_new_char");
}

/*
 *  Delete a character.
 */
MudderyMain.prototype.showDeleteCharacter = function(name, dbref) {
	this.doClosePopupBox();

	var frame_id = "#frame_delete_char";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setData(name, dbref);

	this.showFrame(frame_id);
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

	var frame_ctrl = this.getFrameController("#frame_information");
	frame_ctrl.setInfo(name, icon);
}

/*
 *  Set the player's status.
 */
MudderyMain.prototype.setStatus = function(status) {
	data_handler.character_level = status["level"]["value"];
	$("#prompt_level").text($$("LEVEL: ") + status["level"]["value"]);

	var exp_str = "";
	if (status["max_exp"]["value"] > 0) {
		exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
	}
	else {
		exp_str = "--/--";
	}
	$("#prompt_exp").text($$("EXP: ") + exp_str);

	var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
	$("#prompt_hp").text($$("HP: ") + hp_str);

	var frame_ctrl = this.getFrameController("#frame_information");
	frame_ctrl.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
MudderyMain.prototype.setCombatStatus = function(status) {
	var hp_str = status["hp"] + "/" + status["max_hp"];
	$("#prompt_hp").text($$("HP: ") + hp_str);

	var frame_ctrl = this.getFrameController("#frame_information");
	frame_ctrl.setCombatStatus(status);
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
	var frame_ctrl = this.getFrameController("#frame_information");
	frame_ctrl.setEquipments(equipments);
}
    
/*
 * Set the player's inventory.
 */
MudderyMain.prototype.setInventory = function(inventory) {
	var frame_ctrl = this.getFrameController("#frame_inventory");
	frame_ctrl.setInventory(inventory);
}

/*
 * Set the player's skills.
 */
MudderyMain.prototype.setSkills = function(skills) {
	data_handler.setSkills(skills);

	var frame_ctrl = this.getFrameController("#frame_skills");
	frame_ctrl.setSkills(skills);
}

/* 
 * Set the player's quests.
 */
MudderyMain.prototype.setQuests = function(quests) {
	var frame_ctrl = this.getFrameController("#frame_quests");
	frame_ctrl.setQuests(quests);
}

/*
 * Set the player's current scene.
 */
MudderyMain.prototype.setScene = function(scene) {
	var frame_id = "#frame_scene";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.setScene(scene);
}
    
/*
 * Notify a player has been online.
 */
MudderyMain.prototype.showPlayerOnline = function(player) {
	var frame_id = "#frame_scene";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.addPlayer(player);
}
    
/*
 * Notify a player has been offline.
 */
MudderyMain.prototype.showPlayerOffline = function(player) {
	// If the player is looking to it, close the look window.
	var object_id = "#frame_object";
	if ($(object_id).is(":visible")) {
		var object_ctrl = this.getFrameController(object_id);
		object_ctrl.onObjMovedOut(player["dbref"]);
	}

	var frame_id = "#frame_scene";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.removePlayer(player);
}

/*
 * Notify an object has moved to the player's current place.
 */
MudderyMain.prototype.showObjMovedIn = function(objects) {
	var frame_id = "#frame_scene";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.addObjects(objects);
}

/*
 * Notify an object has moved out the player's current place.
 */
MudderyMain.prototype.showObjMovedOut = function(objects) {
	// If the player is talking to it, close the dialog window.
	var dialogue_id = "#frame_dialogue";
	if ($(dialogue_id).is(":visible")) {
		var dialogue_ctrl = this.getFrameController(dialogue_id);
		object_ctrl.onObjsMovedOut(objects);
	}
        
	// If the player is looking to it, close the look window.
	var object_id = "#frame_object";
	if ($(object_id).is(":visible")) {
		var object_ctrl = this.getFrameController(object_id);
		object_ctrl.onObjsMovedOut(objects);
	}

	// remove objects from scene
	var frame_id = "#frame_scene";
	var frame_ctrl = this.getFrameController(frame_id);
	frame_ctrl.removeObjects(objects);
}

/*
 * Get a frame's controller.
 */
MudderyMain.prototype.getFrameController = function(frame_id) {
    if (frame_id in frameworks) {
        return frameworks[frame_id].controller;
    }
    else {
        var frame = $(frame_id);
        if (frame.length > 0) {
            return frame[0].contentWindow.controller;
        }
    }
}

/*
 * Display a frame.
 */
MudderyMain.prototype.showFrame = function(frame_id) {
	$(frame_id).show();
	$(frame_id).parents().show();
	this.doSetVisiblePopupSize();
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
	this.puppet = false;
	
	controller.showUnlogin();
	controller.doAutoLoginCheck();
}

/*
 * Event when the connection closes.
 */
MudderyMain.prototype.onConnectionClose = function() {
	this.puppet = false;
	
	controller.showConnect();

	// close popup windows
	controller.doClosePopupBox();
	
	// show message
	controller.showMessage($$("Message"), $$("The client connection was closed cleanly."));
}
    
/*
 * Event when the player logins.
 */
MudderyMain.prototype.onLogin = function(data) {
	this.showSelectChar();
}
    
/*
 * Event when the player logs out.
 */
MudderyMain.prototype.onLogout = function(data) {
	this.puppet = false;
	
	// show unlogin UI
	this.showUnlogin();
	
	//reconnect, show the connection screen
	Evennia.connect();
}

/*
 * Event when the player created a new character.
 */
MudderyMain.prototype.onCharacterCreated = function(data) {
	// close popup windows
	controller.doClosePopupBox();
}

/*
 * Event when the player deleted a character.
 */
MudderyMain.prototype.onCharacterDeleted = function(data) {
	// close popup windows
	controller.doClosePopupBox();
}

/*
 * Event when the player puppets a character.
 */
MudderyMain.prototype.onPuppet = function(data) {
	data_handler.character_dbref = data["dbref"];
	data_handler.character_name = data["name"];

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
	this.leftCombatQueue();
}
    
//////////////////////////////////////////
//
// Sizes
//
//////////////////////////////////////////

/*
 * Reset all sizes.
 */
MudderyMain.prototype.doSetSizes = function() {
	controller.doSetWindowSize();
	controller.doSetVisiblePopupSize();
}

/*
 * Reset the sizes of the main window.
 */
MudderyMain.prototype.doSetWindowSize = function() {
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
}

/*
 * Reset the size of a visible popup box.
 */
MudderyMain.prototype.doSetVisiblePopupSize = function() {
	var popup_dialog = $("#popup_container .modal-dialog:visible:first");
	this.setPopupSize(popup_dialog);
}

/*
 * Reset the size of a popup box.
 */
MudderyMain.prototype.setPopupSize = function(dialog) {
	var content = dialog.find(".modal-content");
	if (content.length == 0) {
		return;
	}
	var frame = content.find("iframe");
	if (frame.length == 0) {
		return;
	}

	var height = 0;
	var win_h = $(window).innerHeight();
		
	frame.innerWidth(content.width());
	if (frame.attr("id") == "frame_shop") {
		height = win_h * 0.95;
	}
	else {
		frame.height(0);
	
		var frame_body = frame[0].contentWindow.document.body;	
		height = frame_body.scrollHeight;
		var max_height = win_h * 0.95;
		if (height > max_height) {
			height = max_height;
		}
	}
	
	frame.height(height);	
	dialog.css("top", (win_h - dialog.height()) / 2);
}

/*
 * Reset the size of a visible frame.
 */
MudderyMain.prototype.doChangeVisibleFrameSize = function() {
	var frame = $("#tab_content iframe:visible");
	this.doChangeFrameSize(frame);
}

/*
 * Reset the size of a frame.
 */
MudderyMain.prototype.doChangeFrameSize = function(frame) {
	var tab_content = $("#tab_content");

	frame.width(tab_content.width());
	frame.height(tab_content.height() - 5);
}

//////////////////////////////////////////
//
// Layouts
//
//////////////////////////////////////////

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

	var frame = $("#frame_" + frame_name);
	this.doChangeFrameSize(frame);
	frame.show();
}

/*
 * Show honour tab's content.
 */
MudderyMain.prototype.showHonours = function() {
	this.showContent("honours");
	commands.getRankings();
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
 * Show the layout when players unlogin.
 */
MudderyMain.prototype.showUnlogin = function() {
	// show unlogin UI
	this.clearMsgWindow();
	this.clearPromptBar();

	this.leftCombatQueue();

	// show unlogin tabs
	this.hideTabs();

	$("#tab_register").show();
	$("#tab_login").show();

	this.showContent("login");

	this.clearChannels();
}
    
/*
 * Show the layout when players logged in and going to select a character.
 */
MudderyMain.prototype.showSelectChar = function() {
	//this.clearMsgWindow();
	this.clearPromptBar();

	this.leftCombatQueue();

	// show select character tabs
	this.hideTabs();

	$("#tab_select_char").show();
	$("#tab_system_char").show();

	this.showContent("select_char");

	this.clearChannels();
}

/*
 * Show the layout when players has not connected.
 */
MudderyMain.prototype.showConnect = function() {
	this.hideTabs();
	
	$("#tab_connect").show();
	
	controller.showContent("connect");
	
	this.clearChannels();
}

/*
 * Check the auto login setting.
 */
MudderyMain.prototype.doAutoLoginCheck = function() {

    var playername = "";
    var password = "";
    var save_password = false;
    var auto_login = false;

    if ($.cookie("is_save_password")) {
        save_password = true;
        playername = $.cookie("login_name");
        password = $.cookie("login_password");

        if($.cookie("is_auto_login")) {
            auto_login = true;
        }
    }

    var frame_ctrl = this.getFrameController("frame_login");
	frame_ctrl.setValues(playername, password, save_password, auto_login);

	setTimeout(function(){
		if ($.cookie("is_save_password") && $.cookie("is_auto_login")) {
		    var playername = $.cookie("login_name");
            var playerpassword = $.cookie("login_password");

			$("#cb_auto_login").attr("checked", "true");
			commands.doLogin(playername, playerpassword);
		}
	}, 2000);
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
	
	var message = $("#msg_input").val();
	$("#msg_input").val("");

	if (!message) {
		return;
	}

	if (this.message_type == "cmd") {
		commands.sendRawCommand(message);
	}
	else {
		commands.say(this.message_type, message);
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
	// language
	this.setLanguage(settings["language"]);

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
	var honour_id = "#frame_honours";
	var honour_ctrl = this.getFrameController(honour_id);
	honour_ctrl.setMinHonourLevel(settings["min_honour_level"]);

	// map settings
	var map_id = "#frame_map";
	var map_ctrl = this.getFrameController(map_id);
	map_ctrl.setMap(settings["map_scale"], settings["map_room_size"], settings["map_room_box"]);
}

/*
 * Set the language.
 */
MudderyMain.prototype.setLanguage = function(language) {
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
	this.getFrameController("frame_login").resetLanguage();
	this.getFrameController("#frame_password").resetLanguage();
	this.getFrameController("#frame_map").resetLanguage();
	this.getFrameController("#frame_message").resetLanguage();
	this.getFrameController("#frame_object").resetLanguage();
	this.getFrameController("#frame_quests").resetLanguage();
	this.getFrameController("#frame_register").resetLanguage();
	this.getFrameController("#frame_scene").resetLanguage();
	this.getFrameController("#frame_select_char").resetLanguage();
	this.getFrameController("#frame_shop").resetLanguage();
	this.getFrameController("#frame_honours").resetLanguage();
}

/*
 *  Set the player's all playable characters.
 */
MudderyMain.prototype.setAllCharacters = function(data) {
	var frame_ctrl = this.getFrameController("#frame_select_char");
	frame_ctrl.setCharacters(data);
}
	
/* 
 * Clear all channels' messages.
 */
MudderyMain.prototype.clearChannels = function() {
	$("#msg_type_menu>:not(.template)").remove();
	$("#msg_select").empty();
	$("#msg_type_menu").hide();
	$("#input_bar").css("visibility", "hidden");
}

/*
 * Set available channels.
 */
MudderyMain.prototype.setChannels = function(channels) {
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

			controller.message_type = key;
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
}

/*
 * Set available message types.
 */
MudderyMain.prototype.showMsgTypes = function() {
	if ($("#msg_type_menu>:not(.template)").length == 0) {
		return;
	}

	var button = $("#msg_select");
	var menu = $("#msg_type_menu");

	var left = button.offset().left;
	var top = button.offset().top - menu.outerHeight();

	menu.show();
	menu.offset({top: top, left: left});
}

/*
 * Event when select a message type.
 */
MudderyMain.prototype.selectMsgType = function(caller) {
	controller.message_type = $(caller).data("key");
	$("#msg_select").text($(caller).text());

	$("#msg_type_menu").hide();
}


function refreshWaitingTime() {
    var current_time = new Date().getTime();
    var total_time = Math.floor((current_time - controller.waiting_begin) / 1000);
    $("#prompt_queue").text($$("QUEUE: ") + utils.time_to_string(total_time));
}
