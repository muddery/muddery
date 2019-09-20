

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
// Popup dialogues
//
//////////////////////////////////////////

/*
 * Popup an alert message.
 */
MudderyMain.prototype.showAlert = function(message) {
    this.popupMessage(mudcore.trans("Message"), message);
}

/*
 * Popup a normal message.
 */
MudderyMain.prototype.popupMessage = function(header, content, buttons) {
	this.doClosePopupBox();

	popup_message.setMessage(header, content, buttons);
    popup_message.show();
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
				message_window.displayMessage(mudcore.trans("You got:"));
				first = false;
			}
			message_window.displayMessage(key + ": " + accepted[key]);
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
				message_window.displayMessage(mudcore.trans("You can not get:"));
				first = false;
			}
			message_window.displayMessage(key + ": " + rejected[key]);
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
		popup_get_objects.setObjects(accepted, rejected);
        popup_get_objects.show();
	}
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
 *  Close the popup box.
 */
MudderyMain.prototype.doClosePopupBox = function() {
	$("#popup_container").hide();
	$("#popup_container .modal-dialog").hide();
}


/*
 *  Set the player's status.
 */
MudderyMain.prototype.setStatus = function(status) {
	mudcore.data_handler.character_level = status["level"]["value"];
	prompt_bar.setStatus(status);
	char_data_window.setStatus(status);
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
	self.popupMessage(mudcore.trans("Message"), mudcore.trans("The client connection was closed cleanly."));
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
 * Event when the player puppets a character.
 */
MudderyMain.prototype.onPuppet = function(data) {
    mudcore.data_handler.character_dbref = data["dbref"];
    mudcore.data_handler.character_name = data["name"];

    prompt_bar.setInfo(data["name"], data["icon"]);
    char_data_window.setInfo(data["name"], data["icon"]);
    message_window.clear();

    this.puppet = true;
	this.showPuppet();
}

/*
 * Event when the player unpuppets a character.
 */
MudderyMain.prototype.onUnpuppet = function() {
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
	this.gotoWindow(main_game_window);
}


/*
 * Set the windows stack to a new window.
 */
MudderyMain.prototype.gotoWindow = function(win_controller) {
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
MudderyMain.prototype.popWindow = function(win_controller) {
    if (this.windows_stack.length == 0) {
        console.error("Windows stack is empty.");
        return;
    }

    // Check the last window.
	if (win_controller && win_controller != this.windows_stack[this.windows_stack.length - 1]) {
	    console.error("Windows stack error.");
	    return;
	}

    // Show the last window.
	this.hideAllWindows();
	this.windows_stack.pop();
	var last_controller = this.windows_stack[this.windows_stack.length - 1];
	last_controller.show();

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
    /*
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
	*/
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
 * Popup Message Window.
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupMessage = function(el) {
	BasePopupController.call(this, el);

	this.buttons = [];
}

MudderyPopupMessage.prototype = prototype(BasePopupController.prototype);
MudderyPopupMessage.prototype.constructor = MudderyPopupMessage;

/*
 * Bind events.
 */
MudderyPopupMessage.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
	this.onClick(".popup-footer", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupMessage.prototype.onClose = function(element) {
    this.buttons = [];
    this.el.hide();
    this.select(".header-text").empty();
	this.select(".popup-body").empty();
	this.select(".popup-footer").empty();
}

/*
 * Event when clicks a command button.
 */
MudderyPopupMessage.prototype.onCommand = function(element) {
	var index = $(element).data("index");

	if ("callback" in this.buttons[index]) {
        var callback = this.buttons[index]["callback"];
        if (callback) {
            if ("data" in this.buttons[index]) {
                callback(this.buttons[index]["data"]);
            }
            else {
                callback();
            }
        }
    }

	this.onClose();
}

/*
 * Set message's data.
 */
MudderyPopupMessage.prototype.setMessage = function(header, content, buttons) {
	if (!buttons) {
		buttons = [{"name": mudcore.trans("OK"),
					"callback": null}];
	}
	this.buttons = buttons;

    var header = mudcore.text2html.parseHtml(header) || "&nbsp;";
	this.select(".header-text").html(header);
	this.select(".popup-body").html(mudcore.text2html.parseHtml(content));

    var container = this.select(".popup-footer");
	for (var i = 0; i < buttons.length; i++) {
		var name = mudcore.text2html.parseHtml(buttons[i]["name"]);

		$("<button>").attr("type", "button")
		    .addClass("popup-button")
		    .data("index", i)
			.html(name)
			.appendTo(container);
	}
}


/******************************************
 *
 * Popup Object Window.
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupObject = function(el) {
	BasePopupController.call(this, el);

	this.obj = null;
	this.buttons = [];
}

MudderyPopupObject.prototype = prototype(BasePopupController.prototype);
MudderyPopupObject.prototype.constructor = MudderyPopupObject;

/*
 * Bind events.
 */
MudderyPopupObject.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
	this.onClick(".popup-footer", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupObject.prototype.onClose = function(element) {
    this.object = null;
	this.buttons = [];
    this.el.hide();
    this.select(".header-text").empty();
	this.select(".icon").attr("src", "");
	this.select(".desc").empty();
	this.select(".popup-footer").empty();
}

/*
 * Event when clicks a command button.
 */
MudderyPopupObject.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
		mudcore.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
	}

	this.onClose();
}

/*
 * Event when an object moved out from the current place.
 */
MudderyPopupObject.prototype.onObjMovedOut = function(dbref) {
    if (!this.object) {
        return;
    }

    if (dbref == this.object["dbref"]) {
		this.onClose();
	}
}

/*
 * Event when objects moved out from the current place.
 */
MudderyPopupObject.prototype.onObjsMovedOut = function(objects) {
    if (!this.object) {
        return;
    }

    for (var key in objects) {
        for (var i = 0; i < objects[key].length; i++) {
            if (objects[key][i]["dbref"] == this.object["dbref"]) {
                this.onClose();
                return;
            }
        }
    }
}

/*
 * Set object's data.
 */
MudderyPopupObject.prototype.setObject = function(obj) {
	this.obj = obj;
    var buttons = obj["cmds"]
	if (!buttons) {
		buttons = [{"name": mudcore.trans("OK")}];
	}
	this.buttons = buttons;

	// add name
	this.select("#object_popup_header").html(mudcore.text2html.parseHtml(obj["name"]));

	// add icon
	if (obj["icon"]) {
		var url = settings.resource_url + obj["icon"];
		this.select(".icon").attr("src", url);
		this.select(".icon").show();
    }
    else {
        this.select(".icon").hide();
    }

	// add desc
	desc = mudcore.text2html.parseHtml(obj["desc"]);
	this.select(".desc").html(desc);

    // add buttons
    var container = this.select(".popup-footer");
	for (var i = 0; i < buttons.length; i++) {
		var name = mudcore.text2html.parseHtml(buttons[i]["name"]);

		$("<button>").attr("type", "button")
		    .addClass("popup-button")
		    .data("index", i)
			.html(name)
			.appendTo(container);
	}
}


/******************************************
 *
 * Popup Get Objects Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupGetObjects = function(el) {
	BaseController.call(this, el);
}

MudderyPopupGetObjects.prototype = prototype(BaseController.prototype);
MudderyPopupGetObjects.prototype.constructor = MudderyPopupGetObjects;

/*
 * Bind events.
 */
MudderyPopupGetObjects.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
    this.onClick(".button-ok", this.onClose);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupGetObjects.prototype.onClose = function(element) {
    this.el.hide();
    this.select(".popup-body").empty();
}

/*
 * Set objects that the user get.
 */
MudderyPopupGetObjects.prototype.setObjects = function(accepted, rejected) {
	// set new objects
	var container = this.select(".popup-body");

	for (var name in accepted) {
	    var div = $("<div>")
	        .appendTo(container);

        /*
	    if ("icon" in accepted[name]) {
	        var url = settings.resource_url + accepted[name]["icon"];
	        $("<img>")
	            .addClass("icon")
	            .attr("src", url)
	            .appendTo(div);
	    }
	    */

	    $("<span>")
	        .addClass("item")
	        .html(mudcore.text2html.parseHtml(name + ": " + accepted[name]))
            .appendTo(div);
	}

	for (var name in rejected) {
        var div = $("<div>")
	        .appendTo(container);

        /*
        if ("icon" in rejected[name]) {
            var url = settings.resource_url + rejected[name]["icon"];
            $("<img>")
                .addClass("icon")
                .attr("src", url)
                .appendTo(div);
        }
        */

        $("<span>")
            .addClass("item")
            .html(mudcore.text2html.parseHtml(name + ": " + rejected[name]))
            .appendTo(div);
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

    this.characters = [];
}

MudderySelectChar.prototype = prototype(BaseTabController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick(".button-back", this.onClickBack);
    this.onClick(".button-new-char", this.onNewCharacter);
    this.onClick(".character-list", ".char-name", this.onSelectCharacter);
    this.onClick(".character-list", ".button-delete", this.onDeleteCharacter);
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
    var index = this.select(element).data("index");
    mudcore.service.puppetCharacter(this.characters[index]["dbref"]);
}

/*
 * On delete a character.
 */
MudderySelectChar.prototype.onDeleteCharacter = function(element) {
	var index = this.select(element).data("index");

	var buttons = [
	    {
	        "name": mudcore.trans("Cancel")
	    },
	    {
	        "name": mudcore.trans("Confirm"),
	        "callback": this.confirmDelete,
	        "data": this.characters[index]["dbref"]
	    }
	];
	main_window.popupMessage(mudcore.trans("Warning"),
	                         mudcore.trans("Delete this character?"),
	                         buttons);
}

/*
 * Confirm deleting a character.
 */
MudderySelectChar.prototype.confirmDelete = function(data) {
	var dbref = data;
    mudcore.service.deleteCharacter(dbref);
}

/*
 * Set playable characters.
 */
MudderySelectChar.prototype.setCharacters = function(characters) {
    this.characters = characters;

	var container = this.select(".character-list");
	container.empty();

	for (var i = 0; i < characters.length; i++) {
		var item = $("<div>")
		    .addClass("character-item")
		    .appendTo(container);

		$("<button>")
		    .attr("type", "button")
		    .addClass("button-delete")
			.data("index", i)
			.appendTo(item);

		$("<span>")
		    .addClass("char-name")
			.data("index", i)
			.text(characters[i]["name"])
			.appendTo(item);
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
    main_window.popWindow(new_char_window);
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

/*
 * Event when the player created a new character.
 */
MudderyNewChar.prototype.onCharacterCreated = function(data) {
	// close popup windows
	main_window.popWindow(new_char_window);
}


/******************************************
 *
 * Main Game Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyMainGame = function(el) {
	BaseTabController.call(this, el);
}

MudderyMainGame.prototype = prototype(BaseTabController.prototype);
MudderyMainGame.prototype.constructor = MudderyMainGame;


/******************************************
 *
 * Prompt Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPromptBar = function(el) {
	BaseTabController.call(this, el);
}

MudderyPromptBar.prototype = prototype(BaseTabController.prototype);
MudderyPromptBar.prototype.constructor = MudderyPromptBar;


/*
 * Set character's basic information.
 */
MudderyPromptBar.prototype.setInfo = function(name, icon) {
    this.select(".name").text(name);
    if (icon) {
        var url = settings.resource_url + icon;
        this.select(".icon")
            .attr("src", url)
            .show();
    }
    else {
        this.select(".icon").hide();
    }
}


/*
 * Set character's status.
 */
MudderyPromptBar.prototype.setStatus = function(status) {
    if ("level" in status) {
	    this.select(".level")
	        .text("Lv: " + status["level"]["value"])
	        .show();
	}
	else {
	    this.select(".level").hide();
	}

    if ("exp" in status && "max_exp" in status) {
        var exp_str = "";
        if (status["max_exp"]["value"] > 0) {
            exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
        }
        else {
            exp_str = "--/--";
        }
        this.select(".exp")
            .text("Exp: " + exp_str)
            .show();
    }
    else {
        this.select(".exp").hide();
    }

    if ("hp" in status && "max_hp" in status) {
        var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
        this.select(".hp")
            .text("HP: " + hp_str)
            .show();
    }
    else {
        this.select(".hp").hide();
    }
}

/******************************************
 *
 * Message Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyMessage = function(el) {
	BaseTabController.call(this, el);
}

MudderyMessage.prototype = prototype(BaseTabController.prototype);
MudderyMessage.prototype.constructor = MudderyMessage;


/*
 * Clear messages in message window.
 */
MudderyMessage.prototype.clear = function() {
    this.select(".message-list").empty();
}


/*
 * Display a message in message window.
 */
MudderyMessage.prototype.displayMessage = function(msg, type) {
	var message_list = this.select(".message-list");

	if (!type) {
		type = "normal";
	}

	var item = $("<div>")
		.addClass("msg-" + type)
		.html(msg)
		.appendTo(message_list);

	// remove old messages
	var max = 40;
	var divs = message_list.find("div");
	var size = divs.length;
	if (size > max) {
		divs.slice(0, size - max).remove();
	}

    message_list.stop(true);
    message_list.scrollTop(message_list[0].scrollHeight);
}


/******************************************
 *
 * Character Data Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyCharData = function(el) {
	BaseTabController.call(this, el);
}

MudderyCharData.prototype = prototype(BaseTabController.prototype);
MudderyCharData.prototype.constructor = MudderyCharData;


/*
 * Bind events.
 */
MudderyCharData.prototype.bindEvents = function() {
	this.onClick("#info_box_equipment", "a", this.onLook);
}

/*
 * Event when clicks the object link.
 */
MudderyCharData.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set player's basic data.
 */
MudderyCharData.prototype.setInfo = function(name, icon) {
    this.select(".row-name .name").text(name);
    if (icon) {
        var url = settings.resource_url + icon;
        this.select(".row-name .icon")
            .attr("src", url)
            .show();
    }
    else {
        this.select(".row-name .icon").hide();
    }
}

/*
 * Set player character's information.
 */
MudderyCharData.prototype.setStatus = function(status) {
    this.select(".data-list>tr:not(.row-name)").remove();
    var container = this.select(".data-list");

    var row = $("<tr>");
    for (var key in status) {
        if (key.substring(0, 4) == "max_") {
            var relative_key = key.substring(4);
            if (relative_key in status) {
                // Value and max value will show in the same line, so skip max.
                continue;
            }
        }

        var item = $("<td>");

        var value = status[key]["value"];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in status) {
            // Add max value.
            var max_value = status[max_key]["value"];

            if (max_value == null || typeof(max_value) == "undefined") {
                max_value = "--";
            }
            else if (max_value == 0 && value == 0) {
                value = "--";
                max_value = "--";
            }

            value = value + "/" + max_value;
        }

        item.text(status[key]["name"] + ": " + value);
        row.append(item);

        if (row.children().length == 2) {
            // add a new row
            row.appendTo(container)
            row = $("<tr>");
        }
    }

    if (row.children().length > 0) {
        // add a new row
        row.appendTo(container)
    }
}

/*
 * Set player character's information in combat.
 */
MudderyCharData.prototype.setCombatStatus = function(status) {
    for (var key in status) {
        if (key.substring(0, 4) == "max_") {
            var relative_key = key.substring(4);
            if (relative_key in status) {
                // Value and max value will show in the same line, so skip max.
                continue;
            }
        }

        var item = this.select("#info_" + key);

        var value = status[key];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in status) {
            // Add max value.
            var max_value = status[max_key];

            if (max_value == null || typeof(max_value) == "undefined") {
                max_value = "--";
            }
            else if (max_value == 0 && value == 0) {
                value = "--";
                max_value = "--";
            }

            value = value + "/" + max_value;
        }

        item.find(".attr_value").text(value);
    }
}

/*
 * Set player's equipments.
 */
MudderyCharData.prototype.setEquipments = function(equipments) {
    for (var pos in equipments) {
        var equip = equipments[pos];

        var url = "./img/icon_equipment_block.png";
        var name = "";
        if (equip) {
            if (equip["icon"]) {
                url = settings.resource_url + icon;
            }
            name = mudcore.text2html.parseHtml(equip["name"]);
        }

        this.select(".equipments ." + pos.toLowerCase() + " .icon").attr("src", url);
        this.select(".equipments ." + pos.toLowerCase() + " .name").html(name);
    }
}


/******************************************
 *
 * Inventory Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyInventory = function(el) {
	BaseTabController.call(this, el);

	this.inventory = [];
}

MudderyInventory.prototype = prototype(BaseTabController.prototype);
MudderyInventory.prototype.constructor = MudderyInventory;

/*
 * Bind events.
 */
MudderyInventory.prototype.bindEvents = function() {
	this.onClick("#inv_inventory_items", ".obj_name", this.onLook);
}

/*
 * Event when clicks the object link.
 */
MudderyInventory.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set inventory's data.
 */
MudderyInventory.prototype.setInventory = function(inventory) {
    this.inventory = inventory;

    var container = this.select(".inventory-list");
    container.empty();

    for (var i = 0; i < inventory.length; i++) {
        var obj = inventory[i];
        var row = $("<tr>")
            .data("index", i);

        var cell = $("<td>");

        // icon
        if (obj["icon"]) {
            var div = $("<div>")
                .addClass("icon-div")
                .appendTo(cell);

            var image = $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(div);
        }

        // name
        $("<div>")
            .html(mudcore.text2html.parseHtml(obj["name"]))
            .appendTo(cell);
        cell.appendTo(row);

        // number
        var number = obj["number"];
        if ("equipped" in obj && obj["equipped"]) {
            number += " (equipped)";
        }
        $("<td>")
            .text(number)
            .appendTo(row);

        // desc
        $("<td>")
            .html(mudcore.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        row.appendTo(container);
    }
}


/******************************************
 *
 * Skills Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderySkills = function(el) {
	BaseTabController.call(this, el);

	this.skills = [];
}

MudderySkills.prototype = prototype(BaseTabController.prototype);
MudderySkills.prototype.constructor = MudderySkills;


/*
 * Bind events.
 */
MudderySkills.prototype.bindEvents = function() {
	this.onClick("#skill_list", ".skill_name", this.onLook);
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set skills' data.
 */
MudderySkills.prototype.setSkills = function(skills) {
    this.skills = skills;

    var container = this.select(".skill-list");
    container.empty();

    for (var i = 0; i < skills.length; i++) {
        var obj = skills[i];
        var row = $("<tr>")
            .data("index", i);

        var cell = $("<td>");

        // icon
        if (obj["icon"]) {
            var div = $("<div>")
                .addClass("icon-div")
                .appendTo(cell);

            var image = $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(div);
        }

        // name
        $("<div>")
            .html(mudcore.text2html.parseHtml(obj["name"]))
            .appendTo(cell);
        cell.appendTo(row);

        // desc
        $("<td>")
            .html(mudcore.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        row.appendTo(container);
    }
}


/******************************************
 *
 * Quests Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyQuests = function(el) {
	BaseTabController.call(this, el);

	this.quests = [];
}

MudderyQuests.prototype = prototype(BaseTabController.prototype);
MudderyQuests.prototype.constructor = MudderyQuests;

/*
 * Bind events.
 */
MudderyQuests.prototype.bindEvents = function() {
	this.onClick("#quest_list", ".quest_name", this.onLook);
}

/*
 * Event when clicks the quest link.
 */
MudderyQuests.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set the player's quests.
 */
MudderyQuests.prototype.setQuests = function(quests) {
    this.quests = quests;

    var container = this.select(".quest-list");
    container.empty();

    for (var i = 0; i < quests.length; i++) {
        var obj = quests[i];
        var row = $("<tr>")
            .data("index", i);

        var cell = $("<td>");

        // icon
        if (obj["icon"]) {
            var div = $("<div>")
                .addClass("icon-div")
                .appendTo(cell);

            var image = $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(div);
        }

        // name
        $("<div>")
            .html(mudcore.text2html.parseHtml(obj["name"]))
            .appendTo(cell);
        cell.appendTo(row);

        // desc
        $("<td>")
            .html(mudcore.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        // objectives
        var td = $("<td>");
        for (var j = 0; j < obj["objectives"].length; j++) {
            var objective = obj["objectives"][j];
            var item = $("<p>");
            if ("desc" in objective) {
                item.text(objective["desc"]);
            }
            else {
                item.text(objective["target"] + " " +
                          objective["object"] + " " +
                          objective["accomplished"] + "/" +
                          objective["total"]);
            }
            item.appendTo(td);
        }
        td.appendTo(row);

        row.appendTo(container);
	}
}

/*
 * Add quest's objectives.
 */
MudderyQuests.prototype.addObjectives = function(container, objectives) {
	var template = container.find(".quest_objective>p.template");
	for (var i in objectives) {
		var item = this.cloneTemplate(template);

		if ("desc" in objectives[i]) {
			item.text(objectives[i]["desc"]);
		}
		else {
			item.text(objectives[i]["target"] + " " +
					  objectives[i]["object"] + " " +
					  objectives[i]["accomplished"] + "/" +
					  objectives[i]["total"]);
		}
	}
}


/******************************************
 *
 * Scene Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyScene = function(el) {
	BaseTabController.call(this, el);

    this.max_player = 10;
    this.path_color = "#666";
    this.path_width = "3";

	this.scene = null;
}

MudderyScene.prototype = prototype(BaseTabController.prototype);
MudderyScene.prototype.constructor = MudderyScene;

/*
 * Bind events.
 */
MudderyScene.prototype.bindEvents = function() {
	this.onClick(".scene-commands", "button", this.onCommand);
	this.onClick(".scene-objects", "button", this.onObject);
	this.onClick(".scene-npcs", "button", this.onNPC);
	this.onClick(".scene-players", "button", this.onPlayer);
	this.onClick(".scene-exits", "button", this.onExit);
}

/*
 * On click a command.
 */
MudderyScene.prototype.onCommand = function(element) {
    var index = $(element).data("index");
    var cmd = this.scene["cmds"][index]["cmd_name"];
    var args = this.scene["cmds"][index]["cmd_args"];
    mudcore.service.doCommandLink(cmd, args);
}

/*
 * On look at an object.
 */
MudderyScene.prototype.onObject = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["things"][index]["dbref"];
    dbref = dbref.slice(1);
    mudcore.service.doLook(dbref);
}

/*
 * On look at an NPC.
 */
MudderyScene.prototype.onNPC = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["npcs"][index]["dbref"];
    dbref = dbref.slice(1);
    mudcore.service.doLook(dbref);
}

/*
 * On look at an player.
 */
MudderyScene.prototype.onNPC = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["players"][index]["dbref"];
    dbref = dbref.slice(1);
    mudcore.service.doLook(dbref);
}

/*
 * On go to an exit.
 */
MudderyScene.prototype.onExit = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["exits"][index]["dbref"];
    dbref = dbref.slice(1);
    mudcore.service.doGoto(dbref);
}

/*
 * Clear the view.
 */
MudderyScene.prototype.clearScene = function() {
    this.select(".scene-name").empty();
    this.select(".scene-desc").empty();
    this.select(".scene-commands").empty();
    this.select(".scene-objects").empty();
    this.select(".scene-npcs").empty();
    this.select(".scene-players").empty();
    this.select(".scene-exits td").empty();
    var svg = document.getElementById("exits-svg");
    svg.innerHTML = "";
}

/*
 * Set the scene's data.
 */
MudderyScene.prototype.setScene = function(scene) {
    this.scene = scene;

    this.clearScene();

    // add room's name
    var room_name = mudcore.text2html.parseHtml(scene["name"]);
    this.select(".scene-name").html(">>>>> " + room_name + " <<<<<");

    // add room's desc
    this.select(".scene-desc").html(mudcore.text2html.parseHtml(scene["desc"]));

    // set commands
    var commands = this.select(".scene-commands");
    if ("cmds" in scene && scene["cmds"].length > 0) {
        for (var i = 0; i < scene["cmds"].length; i++) {
            $("<button>")
                .attr("type", "button")
                .data("index", i)
                .text(scene["cmds"][i]["name"])
                .appendTo(commands);
        }
        commands.show();
    }
    else {
        commands.hide();
    }

    // set objects
    var objects = this.select(".scene-objects");
    if ("things" in scene && scene["things"].length > 0) {
        for (var i = 0; i < scene["things"].length; i++) {
            $("<button>")
                .attr("type", "button")
                .data("index", i)
                .text(scene["things"][i]["name"])
                .appendTo(objects);
        }
        objects.show();
    }
    else {
        objects.hide();
    }

    // set npcs
    var npcs = this.select(".scene-npcs");
    if ("npcs" in scene && scene["npcs"].length > 0) {
        for (var i = 0; i < scene["npcs"].length; i++) {
            $("<button>")
                .attr("type", "button")
                .data("index", i)
                .text(scene["npcs"][i]["name"])
                .appendTo(npcs);
        }
        npcs.show();
    }
    else {
        npcs.hide();
    }

    // set players
    var players = this.select(".scene-players");
    if ("players" in scene && scene["players"].length > 0) {
        // Only show 10 players.
        var count = 0;
        for (var i = 0; i < scene["players"].length; i++) {
            $("<button>")
                .attr("type", "button")
                .data("index", i)
                .text(scene["players"][i]["name"])
                .appendTo(players);

            count++
            if (count == this.max_player) {
                break;
            }
        }
        players.show();
    }
    else {
        players.hide();
    }

    // add exits
    if ("exits" in scene && scene["exits"].length > 0) {
        this.setExitsMap(scene["exits"], room_name);
    }

    // set background
    var backview = this.select("#scene-window");
    if ("background" in scene && scene["background"]) {
        var url = settings.resource_url + scene["background"]["resource"];
        backview.css("background", "url(" + url + ") no-repeat center center");
    }
    else {
        backview.css("background", "");
    }
}

/*
 * Add a new player to this scene.
 */
MudderyScene.prototype.addPlayer = function(player) {
    this.addLinks("#scene_players", "#scene_players_container", [player]);
}

/*
 * Remove a player from this scene.
 */
MudderyScene.prototype.removePlayer = function(player) {
    this.select("#scene_obj_" + player["dbref"].slice(1)).remove();

	if (this.select("#scene_players_container>:not(.template)").length == 0) {
	    // No other players.
		this.select("#scene_players").hide();
	}
}

/*
 * Set a mini map of exits.
 */
MudderyScene.prototype.setExitsMap = function(exits, room_name) {
    // sort exits by direction
    // index of direction:
    // 0  1  2
    // 3  4  5
    // 6  7  8
    var room_exits = [];
    if (exits) {
        for (var i = 0;i < exits.length; i++) {
            var direction = mudcore.map_data.getExitDirection(exits[i].key);
            // sort from north (67.5)
            if (direction < 67.5) {
                direction += 360;
            }
            room_exits.push({"data": exits[i],
                             "direction": direction,
                             "index": i
                             });
        }

        room_exits.sort(function(a, b) {return a.direction - b.direction;});
    }

    var exit_grids = [[], [], [] ,[] ,[], [], [], [], []];
    for (var i in room_exits) {
        var index = mudcore.map_data.getDirectionIndex(room_exits[i]["direction"]);
        exit_grids[index].push(room_exits[i]);
    }

    // reverse the upper circle elements
    for (var i = 0; i < 4; ++i) {
        exit_grids[i].reverse();
    }

    // add exits to table
    for (var i = 0; i < exit_grids.length; i++) {
        var position = ".direction-" + i;
        var container = this.select(position);

        if (exit_grids[i].length == 0) {
            var p = $("<p>")
                .appendTo(container);
            p.html("&nbsp;");
            continue;
        }

        for (var j = 0; j < exit_grids[i].length; j++) {
            var exit = exit_grids[i][j];

            var name = "";
            if (exit["data"]["name"]) {
                name = mudcore.text2html.parseHtml(exit["data"]["name"]);
            }

            var p = $("<p>")
                .appendTo(container);

            var button = $("<button>")
                .addClass("exit-" + exit["index"])
                .attr("type", "button")
                .data("index", exit["index"])
                .text(name)
                .appendTo(p);
        }
    }

    // If the center grid is empty, show room's name in the center grid.
    if (exit_grids[4].length == 0) {
        var container = this.select(".direction-4");
        container.text(room_name);
    }

    // draw exit lines
    var svg = document.getElementById("exits-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var center_dom = this.select(".direction-4");
    var x1 = center_dom.position().left + center_dom.outerWidth() / 2;
    var y1 = center_dom.position().top + center_dom.outerHeight() / 2;
    for (var i = 0; i < exits.length; i++) {
        var exit_dom = this.select(".exit-" + i);
        var x2 = exit_dom.position().left + exit_dom.outerWidth() / 2;
        var y2 = exit_dom.position().top + exit_dom.outerHeight() / 2;
        var path = document.createElementNS(namespace, "path");
        path.setAttribute("stroke", this.path_color);
        path.setAttribute("stroke-width", this.path_width);
        path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
        svg.appendChild(path);
    }
}
