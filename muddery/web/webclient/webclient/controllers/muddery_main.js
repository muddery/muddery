
if (typeof(require) != "undefined") {
    require("../css/webclient.css");
    require("../css/webpack.css");

    require("../lang/local_string.js");

    require("../client/client.js");
    require("../client/commands.js");
    require("../utils/map_data.js");
    require("../utils/text2html.js");
    require("../utils/data_handler.js");
    require("../utils/text_escape.js");
    require("../utils/utils.js");
    require("../utils/paginator.js");

    require("../controllers/base_controller.js");
}

/*
 * Derive from the base class.
 */
MudderyMain = function() {
	BaseController.call(this);
	
	this.puppet = false;
    this.solo_mode = false;
	this.message_type = null;
	this.waiting_begin = 0;

	this.resetLanguage();
    this.bindEvents();
	this.doSetWindowSize();
	this.doSetVisiblePopupSize();
	this.el.removeClass("template");
}

MudderyMain.prototype = prototype(BaseController.prototype);
MudderyMain.prototype.constructor = MudderyMain;

/*
 * Document ready event.
 */
MudderyMain.prototype.onReady = function() {
	this.showUnlogin();
    this.showContent("login");
    this.onResize();
}
	
/*
 * Reset the view's language.
 */
MudderyMain.prototype.resetLanguage = function() {
	$("#tab_view_char").text($$.trans("Char"));
	$("#tab_view_social").text($$.trans("Social"));
	$("#tab_view_system").text($$.trans("Sys"));
	$("#tab_view_system_char").text($$.trans("System"));

	$("#tab_button_connect").text($$.trans("Connect"));
	$("#tab_button_login").text($$.trans("Login"));
	$("#tab_button_register").text($$.trans("Register"));
	$("#tab_button_select_char").text($$.trans("Select Char"));
	$("#tab_button_scene").text($$.trans("Scene"));
	$("#tab_button_status").text($$.trans("Status"));
	$("#tab_button_inventory").text($$.trans("Inventory"));
	$("#tab_button_skills").text($$.trans("Skills"));
	$("#tab_button_quests").text($$.trans("Quests"));
	$("#tab_button_honours").text($$.trans("Honours"));
	$("#tab_button_map").text($$.trans("Map"));
	$("#tab_button_logout").text($$.trans("Logout"));
	$("#tab_button_password").text($$.trans("Password"));
	$("#tab_button_logout_puppet").text($$.trans("Logout"));
	$("#tab_button_unpuppet").text($$.trans("Unpuppet"));
	$("#tab_button_password_puppet").text($$.trans("Password"));

	$("#bar_msg_send").text($$.trans("Send"));
}
	
/*
 * Bind events.
 */
MudderyMain.prototype.bindEvents = function() {

    // Event when client window changes
    $(window).bind("resize", this.onResize);

	this.onClick("#tab_button_connect", function(){Evennia.connect()});
    this.onClick("#tab_button_login", function(){$$.main.showContent('login')});
    this.onClick("#tab_button_register", function(){$$.main.showContent('register')});
    this.onClick("#tab_button_select_char", function(){$$.main.showContent('select_char')});
    this.onClick("#tab_button_scene", function(){$$.main.showContent('scene')});
    this.onClick("#tab_button_status", function(){$$.main.showContent('information')});
    this.onClick("#tab_button_inventory", function(){$$.main.showContent('inventory')});
    this.onClick("#tab_button_skills", function(){$$.main.showContent('skills')});
    this.onClick("#tab_button_quests", function(){$$.main.showContent('quests')});
    this.onClick("#tab_button_honours", function(){$$.main.showHonours()});
    this.onClick("#tab_button_map", function(){$$.main.showMap()});
    this.onClick("#tab_button_logout", function(){$$.commands.doLogout()});
    this.onClick("#tab_button_password", function(){$$.main.showContent('password')});
    this.onClick("#tab_button_logout_puppet", function(){$$.commands.doLogout()});
    this.onClick("#tab_button_unpuppet", function(){$$.commands.unpuppetCharacter()});
    this.onClick("#tab_button_password_puppet", function(){$$.main.showContent('password')});
    
    this.onClick("#bar_msg_select", function(){$$.main.showMsgTypes()});
    this.onClick("#bar_msg_send", function(){$$.main.sendMessage()});
    
    this.onClick("#bar_msg_type_menu", "a", function(){controller.selectMsgType(this)});
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
    this.showMessage($$.trans("Message"), message);
}

/*
 * Popup a normal message.
 */
MudderyMain.prototype.showMessage = function(header, content, commands) {
	this.doClosePopupBox();

	var component = $$.component.message;
	component.setMessage(header, content, commands);
    component.show();
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
				this.displayMsg($$.trans("You got:"));
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
				this.displayMsg($$.trans("You can not get:"));
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

	this.doSetVisiblePopupSize();
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
	$("#prompt_queue").text($$.trans("QUEUE: ") + utils.time_to_string(0));
	this.displayMsg($$.trans("You are in queue now. Average waiting time is ") + utils.time_to_string(ave_time) + $$.trans("."));

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

	$$.component.honours.quitCombatQueue();
	$$.component.confirm_combat.closeBox();
}

/*
 * The player has prepared the honour match.
 */
MudderyMain.prototype.prepareMatch = function(data) {
	var component = $$.component.confirm_combat;
	component.setTime(data);
	component.show();

	var popup_dialog = $("#popup_confirm_combat .modal-dialog:visible:first");
	this.setPopupSize(popup_dialog);
}

/*
 * The player has rejected the honour match.
 */
MudderyMain.prototype.matchRejected = function(character_id) {
	$$.component.confirm_combat.closeBox();

	if ("#" + character_id == $$.data_handler.character_dbref) {
		this.displayMsg($$.trans("You have rejected the combat."));
	}
	else {
		this.displayMsg($$.trans("Your opponent has rejected the combat."));
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
	$$.main.doClosePopupBox();
	$$.component.combat_result.show();
}

/*
 * Set the exp the player get.
 */
MudderyMain.prototype.showGetExp = function(exp, combat) {
	// show exp
	this.displayMsg($$.trans("You got exp: ") + exp);

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
 *  Set new character's information.
 */
MudderyMain.prototype.showNewCharacter = function() {
	this.doClosePopupBox();
	$$.component.new_char.show();
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
	$("#prompt_level").text($$.trans("LEVEL: ") + status["level"]["value"]);

	var exp_str = "";
	if (status["max_exp"]["value"] > 0) {
		exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
	}
	else {
		exp_str = "--/--";
	}
	$("#prompt_exp").text($$.trans("EXP: ") + exp_str);

	var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
	$("#prompt_hp").text($$.trans("HP: ") + hp_str);

	$$.component.information.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
MudderyMain.prototype.setCombatStatus = function(status) {
	var hp_str = status["hp"] + "/" + status["max_hp"];
	$("#prompt_hp").text($$.trans("HP: ") + hp_str);

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
	this.puppet = false;
	
	$$.main.showUnlogin();
	$$.main.doAutoLoginCheck();
}

/*
 * Event when the connection closes.
 */
MudderyMain.prototype.onConnectionClose = function() {
	this.puppet = false;
	
	$$.main.showConnect();

	// close popup windows
	$$.main.doClosePopupBox();
	
	// show message
	$$.main.showMessage($$.trans("Message"), $$.trans("The client connection was closed cleanly."));
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
	$$.main.doClosePopupBox();
}

/*
 * Event when the player deleted a character.
 */
MudderyMain.prototype.onCharacterDeleted = function(data) {
	// close popup windows
	$$.main.doClosePopupBox();
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
MudderyMain.prototype.onResize = function() {
	$$.main.doSetWindowSize();
	$$.main.doSetVisiblePopupSize();

	for (var key in $$.component) {
        $$.component[key].onResize();
	}
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

	$("#bar_msg_input").outerWidth($('#middlewindow').width() - 116);
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
	var frame = content.find(">div");
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

		height = frame.find(">div")[0].scrollHeight;
		var max_height = win_h * 0.95;
		if (height > max_height) {
			height = max_height;
		}
	}
	
	frame.height(height);	
	dialog.css("top", (win_h - dialog.height()) / 2);
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
	$$.commands.getRankings();
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
	
	$$.main.showContent("connect");
	
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

    $$.component.login.setValues(playername, password, save_password, auto_login);

	setTimeout(function(){
		if ($.cookie("is_save_password") && $.cookie("is_auto_login")) {
		    var playername = $.cookie("login_name");
            var playerpassword = $.cookie("login_password");

			$("#cb_auto_login").attr("checked", "true");
			$$.commands.doLogin(playername, playerpassword);
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
	
	var message = $("#bar_msg_input").val();
	$("#bar_msg_input").val("");

	if (!message) {
		return;
	}

	if (this.message_type == "cmd") {
		$$.commands.sendRawCommand(message);
	}
	else {
		$$.commands.say(this.message_type, message);
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
	$$.component.honours.setMinHonourLevel(settings["min_honour_level"]);

	// map settings
	$$.component.map.setMap(settings["map_scale"], settings["map_room_size"], settings["map_room_box"]);
}

/*
 * Set the language.
 */
MudderyMain.prototype.setLanguage = function(language) {
	if (!$$.local_string.setLanguage(language)) {
		return;
	}
	
	this.resetLanguage();
	
	for (var key in $$.component) {
        $$.component[key].resetLanguage();
	}
}

/*
 *  Set the player's all playable characters.
 */
MudderyMain.prototype.setAllCharacters = function(data) {
	$$.component.select_char.setCharacters(data);
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

			$$.main.message_type = key;
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
	$$.main.message_type = $(caller).data("key");
	$("#bar_msg_select").text($(caller).text());

	$("#bar_msg_type_menu").hide();
}


function refreshWaitingTime() {
    var current_time = new Date().getTime();
    var total_time = Math.floor((current_time - $$.main.waiting_begin) / 1000);
    $("#prompt_queue").text($$.trans("QUEUE: ") + utils.time_to_string(total_time));
}
