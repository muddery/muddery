
/*
 * Derive from the base class.
 */
MudderyMainFrame = function(el) {
	BaseController.call(this, el);
	
	this.puppet = false;
    this.solo_mode = false;
	this.message_type = null;
	this.waiting_begin = 0;
	this.windows_stack = [];
}

MudderyMainFrame.prototype = prototype(BaseController.prototype);
MudderyMainFrame.prototype.constructor = MudderyMainFrame;


/*
 * Bind events.
 */
MudderyMainFrame.prototype.bindEvents = function() {

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
MudderyMainFrame.prototype.showAlert = function(message) {
    this.popupMessage(core.trans("Message"), message);
}

/*
 * Popup a normal message.
 */
MudderyMainFrame.prototype.popupMessage = function(header, content, buttons) {
	this.doClosePopupBox();

	mud.popup_message.setMessage(header, content, buttons);
    mud.popup_message.show();
}
  
/*  
 * Show shop window.
 */
MudderyMainFrame.prototype.showShop = function(data) {
	this.doClosePopupBox();
	mud.main_game_window.pushWindow(mud.shop_window);
	mud.shop_window.setShop(data);
}

  
/*  
 * Popup shop goods.
 */
MudderyMainFrame.prototype.showGoods = function(dbref, name, number, icon, desc, price, unit) {
	this.doClosePopupBox();

	var component = $$.component.goods;
	component.setGoods(dbref, name, number, icon, desc, price, unit);
	component.show()
}
  
/*  
 * Show get objects messages.
 */
MudderyMainFrame.prototype.showGetObjects = function(accepted, rejected) {
	// show accepted objects
	try {
		var first = true;
		for (var key in accepted) {
			if (first) {
				mud.message_window.displayMessage(core.trans("You got:"));
				first = false;
			}
			mud.message_window.displayMessage(key + ": " + accepted[key]);
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
				mud.message_window.displayMessage(core.trans("You can not get:"));
				first = false;
			}
			mud.message_window.displayMessage(key + ": " + rejected[key]);
		}
	}
	catch(error) {
		console.error(error.message);
	}

    mud.popup_get_objects.setObjects(accepted, rejected);
    mud.popup_get_objects.show();
}
   
/*
 * Show the combat window. 
 */
MudderyMainFrame.prototype.showCombat = function(combat) {
	this.pushWindow(mud.combat_window);
}

/*
 * Close the combat window.
 */
MudderyMainFrame.prototype.closeCombat = function(data) {
	mud.combat_window.finishCombat();
}


/*
 * The combat has finished.
 */
MudderyMainFrame.prototype.finishCombat = function(result) {
	mud.combat_window.finishCombat();
	mud.combat_window.setResult(result);
}


/*
 * Cast a combat skill.
 */
MudderyMainFrame.prototype.setSkillCast = function(result) {
    if ("status" in result && core.data_handler.character_dbref in result["status"]) {
        this.setCombatStatus(result["status"][core.data_handler.character_dbref])
    }

	if (mud.combat_window.isCombatFinished()) {
	    var message = "";
		if ("cast" in result && result["cast"]) {
			message += core.text2html.parseHtml(result["cast"]) + " ";
		}
		if ("result" in result && result["result"]) {
			message += core.text2html.parseHtml(result["result"]);
		}
		if (message) {
			mud.message_window.displayMessage(message);
		}
	}
	else {
		mud.combat_window.setSkillCast(result);
	}
}

/*
 * Set skill's cd.
 */
MudderyMainFrame.prototype.setSkillCD = function(skill, cd, gcd) {
	core.data_handler.setSkillCD(skill, cd, gcd);
	mud.combat_window.setSkillCD(skill, cd, gcd);
}


/*
 * Set the exp the player get.
 */
MudderyMainFrame.prototype.showGetExp = function(exp, combat) {
	// show exp
	mud.message_window.displayMessage(core.trans("You got exp: ") + exp);
}

/*
 *  Close the popup box.
 */
MudderyMainFrame.prototype.doClosePopupBox = function() {
	$("#popup_container").hide();
	$("#popup_container .modal-dialog").hide();
}


/*
 *  Set the player's status.
 */
MudderyMainFrame.prototype.setStatus = function(status) {
	core.data_handler.character_level = status["level"]["value"];
	mud.prompt_bar.setStatus(status);
	mud.char_data_window.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
MudderyMainFrame.prototype.setCombatStatus = function(status) {
	mud.prompt_bar.setStatus(status);
    mud.char_data_window.setCombatStatus(status);
}

//////////////////////////////////////////
//
// Functional Windows
//
//////////////////////////////////////////

/*
 * Notify a player has been online.
 */
MudderyMainFrame.prototype.showPlayerOnline = function(player) {
	$$.component.scene.addPlayer(player);
}
    
/*
 * Notify a player has been offline.
 */
MudderyMainFrame.prototype.showPlayerOffline = function(player) {
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
MudderyMainFrame.prototype.showObjMovedIn = function(objects) {
	$$.component.scene.addObjects(objects);
}

/*
 * Notify an object has moved out the player's current place.
 */
MudderyMainFrame.prototype.showObjMovedOut = function(objects) {
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
MudderyMainFrame.prototype.onConnectionOpen = function() {
    var self = mud.main_frame;
    
	self.puppet = false;

	self.showLoginWindow();
	mud.login_window.checkAutoLogin();
}

/*
 * Event when the connection closes.
 */
MudderyMainFrame.prototype.onConnectionClose = function() {
    var self = mud.main_frame;

	self.puppet = false;

	self.showLoginWindow();

	// close popup windows
	self.doClosePopupBox();
	
	// show message
	self.popupMessage(core.trans("Message"), core.trans("The client connection was closed cleanly."));
}
    
/*
 * Event when the player logins.
 */
MudderyMainFrame.prototype.onLogin = function(data) {
    mud.login_window.onLogin();
	this.showSelectChar();
}
    
/*
 * Event when the player logs out.
 */
MudderyMainFrame.prototype.onLogout = function(data) {
	this.puppet = false;
	
	// show unlogin UI
	this.showLoginWindow();
	
	//reconnect, show the connection screen
	Evennia.connect();
}

/*
 * Event when the player puppets a character.
 */
MudderyMainFrame.prototype.onPuppet = function(data) {
    core.data_handler.character_dbref = data["dbref"];
    core.data_handler.character_name = data["name"];

    mud.prompt_bar.setInfo(data["name"], data["icon"]);
    mud.char_data_window.setInfo(data["name"], data["icon"]);
    mud.message_window.clear();

    this.puppet = true;
	this.showPuppet();
}

/*
 * Event when the player unpuppets a character.
 */
MudderyMainFrame.prototype.onUnpuppet = function() {
    if (!this.puppet) {
        return;
    }
	this.puppet = false;
	this.showSelectChar();
}

/*
 * Reset all sizes.
 */
MudderyMainFrame.prototype.onResize = function() {
}

//////////////////////////////////////////
//
// Layouts
//
//////////////////////////////////////////

MudderyMainFrame.prototype.hideAllWindows = function() {
    $(".popup-window").hide();
    $(".main-window").hide();
}


/*
 * Show the layout when players puppet.
 */
MudderyMainFrame.prototype.showPuppet = function() {
	// show login UI
	this.gotoWindow(mud.main_game_window);
}


/*
 * Set the windows stack to a new window.
 */
MudderyMainFrame.prototype.gotoWindow = function(win_controller) {
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
MudderyMainFrame.prototype.pushWindow = function(win_controller) {
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
MudderyMainFrame.prototype.popWindow = function(win_controller) {
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
 * If the windows is shown.
 */
MudderyMainFrame.prototype.isWindowShow = function(win_controller) {
    if (this.windows_stack.length == 0) {
        return false;
    }

	if (win_controller && win_controller != this.windows_stack[this.windows_stack.length - 1]) {
	    return false;
	}

	return true;
}


/*
 * Show the layout when players unlogin.
 */
MudderyMainFrame.prototype.showLoginWindow = function() {
	// show unlogin UI
	this.gotoWindow(mud.login_window);
}
    
/*
 * Show the layout when players logged in and going to select a character.
 */
MudderyMainFrame.prototype.showSelectChar = function() {
	this.gotoWindow(mud.select_char_window);
}


/*
 * Show the layout when players has not connected.
 */
MudderyMainFrame.prototype.showConnect = function() {
	this.hideTabs();
	
	$("#tab_connect").show();
	
	window_main.showContent("connect");
	
	this.clearChannels();
}

/*
 * Command to send out a speech.
 */
MudderyMainFrame.prototype.sendMessage = function() {
	if (!this.puppet) {
		return;
	}
	
	var message = $("#bar_msg_input").val();
	$("#bar_msg_input").val("");

	if (!message) {
		return;
	}

	if (this.message_type == "cmd") {
		core.service.sendRawCommand(message);
	}
	else {
		core.service.say(this.message_type, message);
	}
}

/*
 * Set the client.
 */
MudderyMainFrame.prototype.setClient = function(settings) {
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
MudderyMainFrame.prototype.clearChannels = function() {
	$("#bar_msg_type_menu>:not(.template)").remove();
	$("#bar_msg_select").empty();
	$("#bar_msg_type_menu").hide();
	$("#input_bar").css("visibility", "hidden");
}

/*
 * Set available channels.
 */
MudderyMainFrame.prototype.setChannels = function(channels) {
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
MudderyMainFrame.prototype.showMsgTypes = function() {
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
MudderyMainFrame.prototype.selectMsgType = function(caller) {
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
	BaseController.call(this, el);

	this.buttons = [];
}

MudderyPopupMessage.prototype = prototype(BaseController.prototype);
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
		buttons = [{"name": core.trans("OK"),
					"callback": null}];
	}
	this.buttons = buttons;

    var header = core.text2html.parseHtml(header) || "&nbsp;";
	this.select(".header-text").html(header);
	this.select(".popup-body").html(core.text2html.parseHtml(content));

    var container = this.select(".popup-footer");
	for (var i = 0; i < buttons.length; i++) {
		var name = core.text2html.parseHtml(buttons[i]["name"]);

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
	BaseController.call(this, el);

	this.obj = null;
	this.buttons = [];
}

MudderyPopupObject.prototype = prototype(BaseController.prototype);
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
		core.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
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
		buttons = [{"name": core.trans("OK")}];
	}
	this.buttons = buttons;

	// add name
	this.select("#object_popup_header").html(core.text2html.parseHtml(obj["name"]));

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
	desc = core.text2html.parseHtml(obj["desc"]);
	this.select(".desc").html(desc);

    // add buttons
    var container = this.select(".popup-footer");
	for (var i = 0; i < buttons.length; i++) {
		var name = core.text2html.parseHtml(buttons[i]["name"]);

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
	        .html(core.text2html.parseHtml(name + ": " + accepted[name]))
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
            .html(core.text2html.parseHtml(name + ": " + rejected[name]))
            .appendTo(div);
    }
}


/******************************************
 *
 * Popup Dialogue Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupDialogue = function(el) {
	BaseController.call(this, el);

    this.sentences = [];
	this.target = null;
}

MudderyPopupDialogue.prototype = prototype(BaseController.prototype);
MudderyPopupDialogue.prototype.constructor = MudderyPopupDialogue;

/*
 * Bind events.
 */
MudderyPopupDialogue.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
    this.onClick(".popup-footer", ".button-next", this.onNext);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupDialogue.prototype.onClose = function(element) {
    this.el.hide();
    this.select(".img-icon").attr("src", "");
    this.select(".div-dialogue").empty();
}

/*
 * Event when clicks the next button.
 */
MudderyPopupDialogue.prototype.onNext = function(element) {
	var dialogue = this.sentences[0]["dialogue"];
	var sentence = this.sentences[0]["sentence"];
	var npc = this.sentences[0]["npc"];
	if (dialogue) {
		core.service.doDialogue(dialogue, sentence, npc);
	}
}

/*
 * Event when objects moved out from the current place.
 */
MudderyPopupDialogue.prototype.onObjsMovedOut = function(objects) {
    for (var key in objects) {
        for (var i in objects[key]) {
            if (objects[key][i]["dbref"] == this.target) {
                this.onClose();
                return;
            }
        }
    }
}

/*
 * Set dialogue's data.
 */
MudderyPopupDialogue.prototype.setDialogue = function(sentences, escapes) {
    this.sentences = sentences;
    if (!sentences || sentences.length == 0) {
        this.onClose();
        return;
    }

	this.target = sentences[0]["npc"];

	if (sentences[0]["can_close"]) {
		this.select(".button-close").show();
	}
	else {
		this.select(".button-close").hide();
	}

	// speaker
	var speaker = core.text2html.parseHtml(sentences[0]["speaker"]);
	if (!speaker) {
		// placeholder
		speaker = "&nbsp;";
	}
	this.select(".header-text").html(speaker);

	// add icon
	if (sentences["icon"]) {
		this.select(".img-icon").attr("src", settings.resource_url + sentences[0]["icon"]);
		this.select(".div-icon").show();
	}
	else {
		this.select(".div-icon").hide();
	}

	// set contents and buttons
    var container = this.select(".div-dialogue");
    container.empty();
    var footer = this.select(".popup-footer");
    footer.empty();

    if (sentences.length == 1) {
        // Only one sentence.
        var dlg = sentences[0];

        var content = core.text2html.parseHtml(dlg["content"]);
        content = core.text_escape.parse(content, escapes);
        container.html(content);

        $("<button>").attr("type", "button")
            .addClass("popup-button button-next")
            .html(core.trans("Next"))
            .appendTo(footer);
    }
    else {
        for (var i = 0; i < sentences.length; i++) {
            var dlg = sentences[i];

            var content = core.text2html.parseHtml(dlg["content"]);
            content = core.text_escape.parse(content, escapes);

            $("<p>")
                .html(content)
                .appendTo(container);
        }

        $("<button>").attr("type", "button")
            .addClass("popup-button")
            .html(core.trans("Select One"))
            .appendTo(footer);
    }
}


MudderyPopupDialogue.prototype.hasDialogue = function() {
    return (this.sentences && this.sentences.length > 0);
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
    if (this.select(".button-tab-login").hasClass("activate")) {
        return;
    }

    this.select(".button-tab-login").addClass("activate");
    this.select(".button-tab-register").removeClass("activate");
    
    this.select(".login-form").show();
    this.select(".register-form").hide();
}

/*
 * Event when clicks the register tab.
 */
MudderyLogin.prototype.onTabRegister = function(element) {
    if (this.select(".button-tab-register").hasClass("activate")) {
        return;
    }

    this.select(".button-tab-register").addClass("activate");
    this.select(".button-tab-login").removeClass("activate");
    
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

    core.service.register(playername, password, password_verify, true);
    this.clearValues();
}

/*
 * Event on click the login button.
 */
MudderyLogin.prototype.onClickLogin = function(element) {
    var name = this.select(".login-name").val();
    var password = this.select(".login-password").val();
    core.service.login(name, password);
}

/*
 * Event on click the auto login checkbox.
 */
MudderyLogin.prototype.onAutoLogin = function(element) {
    var auto_login = this.select(".checkbox-auto-login").prop("checked");

    if (!auto_login) {
        core.service.doRemoveAutoLogin();
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

        this.login_window.setValues(playername, password, true);
	    core.service.login(playername, playerpassword);
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
	BaseController.call(this, el);

    this.characters = [];
}

MudderySelectChar.prototype = prototype(BaseController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick(".character-list", ".char-name", this.onSelectCharacter);
    this.onClick(".character-list", ".button-delete", this.onDeleteCharacter);

    this.onClick(".button-new-char", this.onNewCharacter);
    this.onClick(".button-password", this.onPassword);
    this.onClick(".button-logout", this.onLogout);
}

/*
 * Event when clicks the password button.
 */
MudderySelectChar.prototype.onPassword = function(element) {
    mud.main_frame.pushWindow(mud.password_window);
}

/*
 * Event when clicks the new character button.
 */
MudderySelectChar.prototype.onNewCharacter = function(element) {
    mud.main_frame.pushWindow(mud.new_char_window);
}

/*
 * Event when clicks the logout button.
 */
MudderySelectChar.prototype.onLogout = function(element) {
    core.service.logout();
    Evennia.reconnect();
    mud.main_frame.showLoginWindow();
}

/*
 * On select a character.
 */
MudderySelectChar.prototype.onSelectCharacter = function(element) {
    var index = this.select(element).data("index");
    core.service.puppetCharacter(this.characters[index]["dbref"]);
}

/*
 * On delete a character.
 */
MudderySelectChar.prototype.onDeleteCharacter = function(element) {
	var index = this.select(element).data("index");

	var buttons = [
	    {
	        "name": core.trans("Cancel")
	    },
	    {
	        "name": core.trans("Confirm"),
	        "callback": this.confirmDelete,
	        "data": this.characters[index]["dbref"]
	    }
	];
	mud.main_frame.popupMessage(core.trans("Warning"),
	                            core.trans("Delete this character?"),
	                            buttons);
}

/*
 * Confirm deleting a character.
 */
MudderySelectChar.prototype.confirmDelete = function(data) {
	var dbref = data;
    core.service.deleteCharacter(dbref);
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
	BaseController.call(this, el);
}

MudderyNewChar.prototype = prototype(BaseController.prototype);
MudderyNewChar.prototype.constructor = MudderyNewChar;

/*
 * Bind events.
 */
MudderyNewChar.prototype.bindEvents = function() {
    this.onClick(".button-cancel", this.onClickBack);
    this.onClick(".button-create", this.onCreate);
}

/*
 * Event when clicks the back button.
 */
MudderyNewChar.prototype.onClickBack = function(element) {
    mud.main_frame.popWindow(this);
}

/*
 * Event when clicks the create button.
 */
MudderyNewChar.prototype.onCreate = function(element) {
	var char_name = this.select(".new-char-name").val();
	core.service.createCharacter(char_name);
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
	mud.main_frame.popWindow(this);
}


/******************************************
 *
 * Change Password Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPassword = function(el) {
    BaseController.call(this, el);
}

MudderyPassword.prototype = prototype(BaseController.prototype);
MudderyPassword.prototype.constructor = MudderyPassword;

/*
 * Bind events.
 */
MudderyPassword.prototype.bindEvents = function() {
    this.onClick(".button-cancel", this.onCancel);
    this.onClick(".button-confirm", this.onConfirm);
}

/*
 * Event when clicks the cancel button.
 */
MudderyPassword.prototype.onCancel = function(element) {
    mud.main_frame.popWindow(this);
}


/*
 * Event when clicks the register button.
 */
MudderyPassword.prototype.onConfirm = function(element) {
    var current = this.select(".current-password").val();
    var password = this.select(".new-password").val();
    var password_verify = this.select(".new-password-verify").val();

    core.service.doChangePassword(current, password, password_verify);
    this.clearValues();
}

/*
 * Clear user inputted values.
 */
MudderyPassword.prototype.clearValues = function() {
    this.select(".current-password").val("");
    this.select(".new-password").val("");
    this.select(".new-password-verify").val("");
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
	BaseController.call(this, el);
}

MudderyMainGame.prototype = prototype(BaseController.prototype);
MudderyMainGame.prototype.constructor = MudderyMainGame;

/*
 * Bind events.
 */
MudderyMainGame.prototype.bindEvents = function() {
    $(window).bind("resize", this.onResize);

    this.onClick(".button-scene", this.onScene);
	this.onClick(".button-map", this.onMap);

    this.onClick(".button-character", this.onCharacter);
    this.onClick(".button-status", this.onStatus);
    this.onClick(".button-inventory", this.onInventory);
    this.onClick(".button-skills", this.onSkills);
    this.onClick(".button-quests", this.onQuests);

    this.onClick(".button-system", this.onSystem);
    this.onClick(".button-logout", this.onLogout);
    this.onClick(".button-unpuppet", this.onUnpuppet);
}

/*
 * Show a window.
 */
MudderyMainGame.prototype.showWindow = function(win_controller) {
    this.select(".contents>div").hide();
    win_controller.show();
}

/*
 * Push a window.
 */
MudderyMainGame.prototype.pushWindow = function(win_controller) {
    win_controller.reset();
    win_controller.show();
}

/*
 * Pop a window.
 */
MudderyMainGame.prototype.popWindow = function(win_controller) {
    win_controller.el.hide();
}

/*
 * Event when the window size changed.
 */
MudderyMainGame.prototype.onResize = function(element) {
    mud.main_game_window.resetSize();
}

/*
 * Event when clicks the scene button.
 */
MudderyMainGame.prototype.onScene = function(element) {
    this.showWindow(mud.scene_window);
}

/*
 * Event when clicks the map button.
 */
MudderyMainGame.prototype.onMap = function(element) {
    this.showWindow(mud.map_window);
    mud.map_window.showMap(core.map_data._current_location);
}


/*
 * Event when clicks the character button.
 */
MudderyMainGame.prototype.onCharacter = function(element) {
    // Show the character menu.
    this.select(".menu-character").toggleClass("hidden");
}

/*
 * Event when clicks the status button.
 */
MudderyMainGame.prototype.onStatus = function(element) {
    this.select(".menu-character").addClass("hidden");
    this.showWindow(mud.char_data_window);
}

/*
 * Event when clicks the inventory button.
 */
MudderyMainGame.prototype.onInventory = function(element) {
    this.select(".menu-character").addClass("hidden");
    this.showWindow(mud.inventory_window);
}

/*
 * Event when clicks the skills button.
 */
MudderyMainGame.prototype.onSkills = function(element) {
    this.select(".menu-character").addClass("hidden");
    this.showWindow(mud.skills_window);
}

/*
 * Event when clicks the character button.
 */
MudderyMainGame.prototype.onQuests = function(element) {
    this.select(".menu-character").addClass("hidden");
    this.showWindow(mud.quests_window);
}


/*
 * Event when clicks the system button.
 */
MudderyMainGame.prototype.onSystem = function(element) {
    // Show the character menu.
    this.select(".menu-system").toggleClass("hidden");
}

/*
 * Event when clicks the logout button.
 */
MudderyMainGame.prototype.onLogout = function(element) {
    this.select(".menu-system").addClass("hidden");

    core.service.logout();
    Evennia.reconnect();
    mud.main_frame.showLoginWindow();
}

/*
 * Event when clicks the unpuppet button.
 */
MudderyMainGame.prototype.onUnpuppet = function(element) {
    this.select(".menu-system").addClass("hidden");

	core.service.unpuppetCharacter();
	mud.main_frame.onUnpuppet();
}

/*
 * Set popup menus position.
 */
MudderyMainGame.prototype.resetSize = function(element) {
    // Character menu.
    var button_char = this.select(".button-character");
    var menu_char = this.select(".menu-character");
    var pos_char = {
        left: button_char.position().left,
        top: button_char.position().top - menu_char.height() - 5
    }
    menu_char.css(pos_char);

    // System menu.
    var button_sys = this.select(".button-system");
    var menu_sys = this.select(".menu-system");
    var pos_sys = {
        left: button_sys.position().left,
        top: button_sys.position().top - menu_sys.height() - 5
    }
    menu_sys.css(pos_sys);
}

/******************************************
 *
 * Prompt Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPromptBar = function(el) {
	BaseController.call(this, el);
}

MudderyPromptBar.prototype = prototype(BaseController.prototype);
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
	BaseController.call(this, el);
}

MudderyMessage.prototype = prototype(BaseController.prototype);
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
	BaseController.call(this, el);
}

MudderyCharData.prototype = prototype(BaseController.prototype);
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
    var dbref = $(element).data("dbref");
    core.service.doLook(dbref);
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
            name = core.text2html.parseHtml(equip["name"]);
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
	BaseController.call(this, el);

	this.inventory = [];
}

MudderyInventory.prototype = prototype(BaseController.prototype);
MudderyInventory.prototype.constructor = MudderyInventory;

/*
 * Bind events.
 */
MudderyInventory.prototype.bindEvents = function() {
}

/*
 * Event when clicks the object link.
 */
MudderyInventory.prototype.onLook = function(element) {
    var index = $(element).data("index");
    if (index < this.inventory.length) {
        var dbref = this.inventory[index].dbref;
        core.service.doLook(dbref);
    }
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
            .addClass("object-row")
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
            .html(core.text2html.parseHtml(obj["name"]))
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
            .html(core.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        row.appendTo(container);
    }

    this.onClick(".object-row", this.onLook);
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
	BaseController.call(this, el);

	this.skills = [];
}

MudderySkills.prototype = prototype(BaseController.prototype);
MudderySkills.prototype.constructor = MudderySkills;


/*
 * Bind events.
 */
MudderySkills.prototype.bindEvents = function() {
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onLook = function(element) {
    var index = $(element).data("index");
    if (index < this.skills.length) {
        var dbref = this.skills[index].dbref;
        core.service.doLook(dbref);
    }
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
            .addClass("object-row")
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
            .html(core.text2html.parseHtml(obj["name"]))
            .appendTo(cell);
        cell.appendTo(row);

        // desc
        $("<td>")
            .html(core.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        row.appendTo(container);
    }

	this.onClick(".object-row", this.onLook);
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
	BaseController.call(this, el);

	this.quests = [];
}

MudderyQuests.prototype = prototype(BaseController.prototype);
MudderyQuests.prototype.constructor = MudderyQuests;

/*
 * Bind events.
 */
MudderyQuests.prototype.bindEvents = function() {
}

/*
 * Event when clicks the quest link.
 */
MudderyQuests.prototype.onLook = function(element) {
    var index = $(element).data("index");
    if (index < this.quests.length) {
        var dbref = this.quests[index].dbref;
        core.service.doLook(dbref);
    }
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
            .addClass("object-row")
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
            .html(core.text2html.parseHtml(obj["name"]))
            .appendTo(cell);
        cell.appendTo(row);

        // desc
        $("<td>")
            .html(core.text2html.parseHtml(obj["desc"]))
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

	this.onClick(".object-row", this.onLook);
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
	BaseController.call(this, el);

    this.max_player = 10;
    this.path_color = "#666";
    this.path_width = "3";

	this.scene = null;
}

MudderyScene.prototype = prototype(BaseController.prototype);
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

    !function(caller, method) {
		$(window).on("resize", undefined, caller, function(event) {
    		method.call(event.data, event.currentTarget, event);
    	});
    }(this, this.onResize);
}

/*
 * On click a command.
 */
MudderyScene.prototype.onCommand = function(element) {
    var index = $(element).data("index");
    var cmd = this.scene["cmds"][index]["cmd_name"];
    var args = this.scene["cmds"][index]["cmd_args"];
    core.service.doCommandLink(cmd, args);
}

/*
 * On look at an object.
 */
MudderyScene.prototype.onObject = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["things"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.doLook(dbref);
}

/*
 * On look at an NPC.
 */
MudderyScene.prototype.onNPC = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["npcs"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.doLook(dbref);
}

/*
 * On look at an player.
 */
MudderyScene.prototype.onPlayer = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["players"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.doLook(dbref);
}

/*
 * On go to an exit.
 */
MudderyScene.prototype.onExit = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["exits"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.doGoto(dbref);
}

/*
 * On the window resize.
 */
MudderyScene.prototype.onResize = function() {
    this.resetSize();
}

/*
 * Set element's size.
 */
MudderyScene.prototype.resetSize = function() {
    var svg = document.getElementById("exits-svg");
    svg.innerHTML = "";

    if (this.scene && "exits" in this.scene) {
        this.drawExitPaths(this.scene["exits"]);
    }
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
    var room_name = core.text2html.parseHtml(scene["name"]);
    this.select(".scene-name").html(">>>>> " + room_name + " <<<<<");

    // add room's desc
    this.select(".scene-desc").html(core.text2html.parseHtml(scene["desc"]));

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
            var direction = core.map_data.getExitDirection(exits[i].key);
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
        var index = core.map_data.getDirectionIndex(room_exits[i]["direction"]);
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
                name = core.text2html.parseHtml(exit["data"]["name"]);
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

    this.drawExitPaths(exits);
}

/*
 * Draw exit paths.
 */
MudderyScene.prototype.drawExitPaths = function(exits) {
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


/******************************************
 *
 * Map Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyMap = function(el) {
	BaseController.call(this, el);

    // the size of a room
    this.room_size = 40;
}

MudderyMap.prototype = prototype(BaseController.prototype);
MudderyMap.prototype.constructor = MudderyMap;

/*
 * Bind events.
 */
MudderyMap.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
}

/*
 * Set element's size.
 */
MudderyMap.prototype.resetSize = function() {

}

/*
 * Event when clicks the close button.
 */
MudderyMap.prototype.onClose = function(element) {
    this.el.hide();
}

/*
 * Clear the map.
 */
MudderyMap.prototype.clear = function() {
    this.select(".header-text").html(core.trans("Map"));
    var svg = document.getElementById("map-svg");
    svg.innerHTML = "";
}

/*
 * Show current location's map.
 */
MudderyMap.prototype.showMap = function(location) {
	this.clear();

	if (!(location && location.key in core.map_data._map_rooms)){
		// does not have current location, can not show map.
		return;
	}

	if (location["area"]) {
		var area_name = core.text2html.parseHtml(location["area"]["name"]);
		if (area_name) {
			this.select(".header-text").html(area_name);
		}
	}

	var current_room = core.map_data._map_rooms[location.key];

	var map_width = this.select(".map-body").width();
	var map_height = this.select(".map-body").height();

	// var scale = this.scale;
	var room_size = this.room_size;
	var origin_x = map_width / 2;
	var origin_y = map_height / 2;
	var current_area_key = "";		// Only show rooms and exits in the same area.

	var svg = document.getElementById("map-svg");
	var namespace = "http://www.w3.org/2000/svg";

	if (current_room["pos"]) {
		// set origin point
		//origin_x -= current_room["pos"][0] * scale;
		//origin_y -= -current_room["pos"][1] * scale;
		origin_x -= current_room["pos"][0];
		origin_y -= current_room["pos"][1];

		current_area_key = current_room["area"];
	}

	// background
	if (location["area"] && location["area"]["background"]) {
        var x = origin_x;
        var y = origin_y;

        /*
        if (location["area"]["background_point"]) {
            x -= location["area"]["background_point"][0];
            y -= location["area"]["background_point"][1];
        }

        if (location["area"]["corresp_map_pos"]) {
            x += location["area"]["corresp_map_pos"][0] * scale + origin_x;
            y += -location["area"]["corresp_map_pos"][1] * scale + origin_y;
        }
        */

        var map_back = settings.resource_url + location["area"]["background"]["resource"];
        var background = document.createElementNS(namespace, "image");
        background.setAttribute("x", x);
        background.setAttribute("y", y);
        background.setAttribute("width", location["area"]["background"]["width"]);
        background.setAttribute("height", location["area"]["background"]["height"]);
        background.href.baseVal = settings.resource_url + location["area"]["background"]["resource"];
        svg.appendChild(background);
	}

	if (current_room["pos"] && core.map_data._map_paths) {
		// get path positions
		var path_data = [];
		for (var begin in core.map_data._map_paths) {
			if (!(begin in core.map_data._map_rooms)) {
			    continue;
			}

            var from_room = core.map_data._map_rooms[begin];
            var from_area_key = from_room["area"];
            if (from_area_key != current_area_key) {
                continue;
            }

            var from = from_room["pos"];
            if (!from) {
                continue;
            }

            for (var end in core.map_data._map_paths[begin]) {
                if (!(core.map_data._map_paths[begin][end] in core.map_data._map_rooms)) {
                    continue;
                }

                var to_room = core.map_data._map_rooms[core.map_data._map_paths[begin][end]];
                var to_area_key = to_room["area"];
                if (to_area_key != current_area_key) {
                    continue;
                }

                var to = to_room["pos"];
                if (!to) {
                    continue;
                }

                path_data.push({"from": from, "to": to});  // path posision
            }
        }

        // draw path
        for (var i = 0; i < path_data.length; i++) {
            var from = path_data[i]["from"];
            var to = path_data[i]["to"];

            var path = document.createElementNS(namespace, "line");
            path.setAttribute("x1", from[0] + origin_x);
            path.setAttribute("y1", from[1] + origin_y);
            path.setAttribute("x2", to[0] + origin_x);
            path.setAttribute("y2", to[1] + origin_y);
            path.setAttribute("stroke", "grey");
            path.setAttribute("stroke-width", "2");
            svg.appendChild(path);
		}
	}

	if (core.map_data._map_rooms) {
		// get room positions
		var room_data = [];
		var current_room_index = -1;

		if (current_room["pos"]) {
			var count = 0;
			for (var key in core.map_data._map_rooms) {
				var room = core.map_data._map_rooms[key];
				if (room["pos"]) {
					var area_key = room["area"];
					if (area_key != current_area_key) {
						continue;
					}

					room_data.push({"name": core.utils.truncate_string(room["name"], 10, true),
									"icon": room["icon"]? settings.resource_url + room["icon"]: null,
									"area": room["area"],
									"pos": room["pos"]});
					if (key == location.key) {
						current_room_index = count;
					}
					count++;
				}
			}
		}
		else {
			// does not have current position, only show current room at center.
			room_data.push({"name": core.utils.truncate_string(current_room["name"], 10, true),
							"icon": current_room["icon"]? settings.resource_url + current_room["icon"]: null,
							"area": current_room["area"],
							"pos": [0, 0]});
			current_room_index = 0;
		}

        // draw room
        for (var i = 0; i < room_data.length; i++) {
            var room = room_data[i];

            // draw icon
            if (room["icon"]) {
                var icon = document.createElementNS(namespace, "image");
                icon.setAttribute("x", room["pos"][0] - room_size / 2 + origin_x);
                icon.setAttribute("y", room["pos"][1] - room_size / 2 + origin_y);
                icon.setAttribute("width", room_size);
                icon.setAttribute("height", room_size);
                icon.href.baseVal = room["icon"];
                svg.appendChild(icon);
            }

            // draw room's name
            if (room["name"]) {
                var name = document.createElementNS(namespace, "text");
                name.setAttribute("x", room["pos"][0] + origin_x);
                name.setAttribute("y", room["pos"][1] + origin_y);
                name.setAttribute("dy", room["icon"] ? room_size / 2 + 16 : 8);
                name.setAttribute("text-anchor", "middle");
                name.setAttribute("font-family", "sans-serif");
                name.setAttribute("font-size", (i == current_room_index)? "14px": "12px");
                name.setAttribute("fill", (i == current_room_index)? "white": "#eee");
                name.setAttribute("style", "text-shadow: .1em .1em .5em #000000;");
                name.textContent = core.text2html.clearTags(room["name"]);
                svg.appendChild(name);
            }
        }
	}
}


/******************************************
 *
 * Combat Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyCombat = function(el) {
	BaseController.call(this, el);

	this.self_dbref = "";
	this.target = "";
	this.interval_id = null;
	this.timeout = 0;
	this.timeline = 0;
	this.combat_finished = true;
	this.skill_cd_time = {};
}

MudderyCombat.prototype = prototype(BaseController.prototype);
MudderyCombat.prototype.constructor = MudderyCombat;

/*
 * Bind events.
 */
MudderyCombat.prototype.bindEvents = function() {
	this.onClick(".combat-buttons", "button", this.onCombatSkill);
	this.onClick(".result-button-ok", this.onClose);
}

/*
 * Event when clicks a skill button.
 */
MudderyCombat.prototype.onCombatSkill = function(element) {
	if (this.combat_finished) {
		return;
	}

	var key = $(element).data("key");

	// Check CD.
	if (key in this.skill_cd_time) {
		var cd_time = this.skill_cd_time[key];
		var current_time = new Date().getTime();
		if (cd_time > current_time) {
			return;
		}
	}

	core.service.doCastSkill(key, this.target, true);
}


/*
 * Event when clicks the close button.
 */
MudderyCombat.prototype.onClose = function(element) {
	// close popup box
    mud.main_frame.popWindow(this);

    if (mud.popup_dialogue.hasDialogue()) {
        mud.popup_dialogue.show();
    }
}


/*
 * Reset the combat box.
 */
MudderyCombat.prototype.reset = function(skill_cd_time) {
	this.select(".combat-desc").empty();

	// Remove characters that are not template.
	this.select(".combat-characters").empty();

	// Remove combat messages.
	this.select(".combat-messages").empty();

	// Remove skill buttons that are not template.
	this.select(".combat-buttons").empty();;

	this.self_dbref = "";
	this.target = "";
	this.combat_finished = true;
	this.skill_cd_time = core.data_handler.skill_cd_time;
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}

	// Clear combat results.
	this.select(".combat-result").hide();

    this.select(".result-header").empty();

    this.select(".result-exp-block").hide();
    this.select(".result-exp").empty();
    this.select(".result-accepted").hide();
    this.select(".result-accepted-list").empty();
    this.select(".result-rejected").hide();
    this.select(".result-rejected-list").empty();
}

/*
 * Set combat data.
 */
MudderyCombat.prototype.setCombat = function(desc, timeout, characters, self_dbref) {
	if (!this.combat_finished) {
		return;
	}
	this.combat_finished = false;

	this.self_dbref = self_dbref;

	var self_team = "";
	for (var i in characters) {
		if (characters[i]["dbref"] == self_dbref) {
			self_team = characters[i]["team"];
		}
	}

	// add desc
	this.select(".combat-desc").html(core.text2html.parseHtml(desc));

	// add timeout
	if (timeout > 0) {
		var current_time = new Date().getTime();
		this.timeout = timeout;
		this.timeline = current_time + timeout * 1000;

		this.select(".combat-timeout").text(timeout);
		this.select(".combat-time-div").show();
		this.interval_id = window.setInterval("mud.combat_window.refreshTimeout()", 1000);
	}
	else {
		this.select(".combat-timeout").empty();
		this.select(".combat-time-div").hide();
	}

	// add characters
	var teammate_number = 0;
	var enemy_number = 0;
	var top = 10;
	var line_height = 30;

	var status = {};
	for (var i in characters) {
		var character = characters[i];
		var dbref = character["dbref"];
		status[dbref] = character;

		var item = $("<div>")
            .attr("id", "combat-char-" + dbref.slice(1))
        	.data("dbref", character["dbref"]);

        $("<div>")
            .addClass("status")
            .appendTo(item);

		if (character["icon"]) {
		    var div_icon = $("<div>")
		        .addClass("div-icon")
		        .appendTo(item);

		    $("<img>")
		        .addClass("character-icon")
			    .attr("src", settings.resource_url + character["icon"])
			    .appendTo(div_icon);
		}

        $("<div>")
            .addClass("name")
		    .text(character["name"]);

		if (this.self_dbref == dbref) {
		    this.select(".prompt-bar>.name").text(character["name"]);
		}

		if (character["team"] == self_team) {
			item.addClass("teammate")
			   .css('top', top + teammate_number * line_height);
			teammate_number++;
		}
		else {
			item.addClass("enemy")
			   .css('top', top + enemy_number * line_height);
			enemy_number++;

			if (!this.target) {
				// Set default target.
				this.target = character["dbref"];
			}
		}

		item.appendTo(this.select(".combat-characters"));
	}

	this.updateStatus(status);
}

/*
 * Set combat commands.
 */
MudderyCombat.prototype.setCommands = function(commands) {
	var left = 10;
	var top = 10;
	var line = 4;
	var width = 70;
	var line_height = 80;

	if (commands) {
		for (var i in commands) {
			var command = commands[i];

			var item = $("<button>")
			    .addClass("btn-combat")
			    .attr("type", "button")
                .attr("id", "cmd-" + command["key"])
				.data("key", command["key"])
				.data("cd", 0)
				.css({"left": left + i % line * width,
					  "top": top + parseInt(i / line) * line_height});

			if (command["icon"]) {
			    var div_icon = $("<div>")
			        .appendTo(item);

                $("<img>")
                    .addClass("command-icon")
				    .attr("src", settings.resource_url + command["icon"])
				    .appendTo(item);
			}

            $("<div>")
                .addClass("command-name")
                .html(core.text2html.parseHtml(command["name"]))
                .appendTo(item);

            $("<div>")
                .addClass("cooldown")
                .appendTo(item);

            item.appendTo(this.select(".combat-buttons"));
		}

		this.select(".combat-buttons").height(5 + parseInt((commands.length - 1) / line + 1) * line_height)
	}
}

/*
 * Cast a skill in the combat.
 */
MudderyCombat.prototype.setSkillCast = function(data) {
	if (this.combat_finished) {
		return;
	}

	var message = "";
	if ("cast" in data && data["cast"]) {
	    message += core.text2html.parseHtml(data["cast"]) + " ";
	}
	if ("result" in data && data["result"]) {
		message += core.text2html.parseHtml(data["result"]);
	}
	if (message) {
		this.displayMsg(message);
	}

	if ("skill" in data) {
		if (data["skill"] == "skill_normal_hit" ||
			data["skill"] == "skill_dunt") {

			var caller = $('#combat-char-' + data["caller"].slice(1));
			if (caller.hasClass("teammate")) {
				caller.animate({left: '50%'}, 100);
				caller.animate({left: '12%'}, 100);
			}
			else {
				caller.animate({right: '50%'}, 100);
				caller.animate({right: '12%'}, 100);
			}
		}
		else if (data["skill"] == "skill_normal_heal" ||
				 data["skill"] == "skill_powerful_heal") {
		}
		else if (data["skill"] == "skill_escape") {
			if (data["data"] == 1) {
				var item_id = "#combat-char-" + data["target"].slice(1) + ".status";
				$(item_id).text(core.trans("Escaped"));
			}
		}
	}

	// Update status.
	if ("status" in data) {
		this.updateStatus(data["status"]);
	}
}

/*
 * Display a message in message window.
 */
MudderyCombat.prototype.displayMsg = function(msg) {
	var msg_wnd = this.select(".combat-messages");
	if (msg_wnd.length > 0) {
		msg_wnd.stop(true);
		msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
	}

	var item = $("<div>")
	    .addClass("msg")
	    .addClass("msg-normal")
		.html(msg)
		.appendTo(msg_wnd);

	// remove old messages
	var divs = msg_wnd.find("div");
	var max = 10;
	var length = divs.length;
	if (length > max) {
		divs.slice(0, length - max).remove();
	}

	// scroll message window to bottom
	msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
}

/*
 * Update character's status.
 */
MudderyCombat.prototype.updateStatus = function(status) {
	for (var key in status) {
		var item_id = "#combat-char-" + key.slice(1) + ">div.status";
		$(item_id).text(status[key]["hp"] + "/" + status[key]["max_hp"]);

		if (this.self_dbref == key) {
		    $("#combat_status").text("HP:" + status[key]["hp"] + "/" + status[key]["max_hp"]);
		}
	}
}

/*
 * Set skill's CD.
 */
MudderyCombat.prototype.setSkillCD = function(skill, cd, gcd) {
	if (this.combat_finished) {
		return;
	}

	// update skill's cd
	var current_time = new Date().getTime();

	// cd_time in milliseconds
	var cd_time = current_time + cd * 1000;
	if (skill in this.skill_cd_time) {
		if (this.skill_cd_time[skill] < cd_time) {
			this.skill_cd_time[skill] = cd_time;
		}
	}
	else {
		this.skill_cd_time[skill] = cd_time;
	}

	var gcd_time = current_time + gcd * 1000;
	for (var key in this.skill_cd_time) {
		if (this.skill_cd_time[key] < gcd_time) {
			this.skill_cd_time[key] = gcd_time;
		}
	}

	// refresh button's CD
	this.select(".combat-buttons>button").each(function() {
        this.showButtonCD(this);
    });
}

/*
 * Show skill's CD.
 */
MudderyCombat.prototype.showButtonCD = function(button_id) {
	var button = $(button_id);
	var cooldown = button.find(">.cooldown");

	var key = button.data("key");

	var cd_time = 0;
	if (key in this.skill_cd_time) {
		cd_time = this.skill_cd_time[key];
	}

	var current_cd = button.data("cd");
	if (current_cd >= cd_time) {
		return;
	}

	var current_time = new Date().getTime();

	cooldown.stop(true, true);
	if (current_cd < current_time) {
		// set a new cd
		cooldown.css("height", "100%")
			.css("top", 0);
	}

	cooldown.animate({height: "0%", top: "100%"}, cd_time - current_time, "linear");
	button.data("cd", cd_time);
}

/*
 * Finish a combat.
 */
MudderyCombat.prototype.finishCombat = function(result) {
	this.combat_finished = true;
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}
}

/*
 * Finish a combat.
 */
MudderyCombat.prototype.isCombatFinished = function() {
    return this.combat_finished;
}


/*
 * Set result data.
 */
MudderyCombat.prototype.setResult = function(result) {
	this.select(".combat-result").show();

	if (!result) {
		return;
	}

	var header = "";
	if ("escaped" in result) {
	   header = core.trans("Escaped !");
	}
	else if ("win" in result) {
		header = core.trans("You win !");
	}
	else if ("lose" in result) {
		header = core.trans("You lost !");
	}
	else if ("draw" in result) {
		header = core.trans("Draw !");
	}

	this.select(".result-header").text(header);

    if ("exp" in result) {
        this.setGetExp(result["exp"]);
    }

    if ("get_objects" in result) {
    	this.setGetObjects(result["get_objects"]);
    }
}


/*
 * Set the experiences that the player get.
 */
MudderyCombat.prototype.setGetExp = function(exp) {
	this.select(".result-exp").text(exp);
}


/*
 * Set the objects that the player get.
 */
MudderyCombat.prototype.setGetObjects = function(get_objects) {
    if (get_objects["accepted_names"] && Object.keys(get_objects["accepted_names"]).length > 0) {
	    this.setItems(".result-accepted-list", get_objects["accepted_names"]);
	    this.select(".result-accepted").show();
	}

	if (get_objects["reject_reason"] && Object.keys(get_objects["reject_reason"]).length > 0) {
	    this.setItems(".result-rejected-list", get_objects["reject_reason"]);
	    this.select(".result-rejected").show();
	}
}

/*
 * Set object items.
 */
MudderyCombat.prototype.setItems = function(container_id, objects) {
    var container = this.select(container_id);
    for (var name in objects) {
        var item = $("<p>")
            .appendTo(container);

        $("<span>")
            .addClass("name")
            .text(name)
            .appendTo(item);

        $("<span>")
            .addClass("info")
            .text(objects[name])
            .appendTo(item);
    }
}

/*
 * Calculate the remain time of the combat.
 */
MudderyCombat.prototype.refreshTimeout = function() {
    var current_time = new Date().getTime();

    var remain = Math.ceil((this.timeline - current_time) / 1000);
    if (remain > this.timeout) {
        remain = this.timeout;
    }
    if (remain < 0) {
        remain = 0;
    }

    $("#combat-window .combat-timeout").text(remain);
};


/******************************************
 *
 * Shop Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyShop = function(el) {
	BaseController.call(this, el);

	this.goods = [];
}

MudderyShop.prototype = prototype(BaseController.prototype);
MudderyShop.prototype.constructor = MudderyShop;

/*
 * Bind events.
 */
MudderyShop.prototype.bindEvents = function() {
	// close popup box
    this.onClick(".button-close", this.onClose);
}

 /*
 * Event when clicks the close button.
 */
MudderyShop.prototype.onClose = function(element) {
	// close popup box
    mud.main_game_window.popWindow(this);
}

/*
 * Reset the shop
 */
MudderyShop.prototype.reset = function() {
	this.select(".header-text").html("Shop");
    this.select(".shop-icon-img")
        .attr("src", "")
        .hide();
    this.select(".shop-desc").html("");
    this.select(".goods-list").empty();
}


/*
 * Event when clicks the object link.
 */
MudderyShop.prototype.onLook = function(element) {
    var index = $(element).data("index");
    if (index < this.goods.length) {
        var goods = this.goods[index];
        mud.main_game_window.pushWindow(mud.goods_window);
        mud.goods_window.setGoods(goods);
    }
}


/*
 * Set shop's goods.
 */
MudderyShop.prototype.setShop = function(data) {
    var name = data["name"];
    var icon = data["icon"];
    var desc = data["desc"];
	this.goods = data["goods"] || [];

	// add name
	this.select(".header-text").html(core.text2html.parseHtml(name));

	// add icon
    if (icon) {
        var url = settings.resource_url + icon;
        this.select(".shop-icon-img")
            .attr("src", url)
            .show();
    }
    else {
        this.select(".shop-icon-img").hide();
    }

	// add desc
	this.select(".shop-desc").html(core.text2html.parseHtml(desc));

	// set goods
	var container = this.select(".goods-list");
	for (var i in this.goods) {
		var obj = this.goods[i];
        var row = $("<tr>")
            .addClass("goods-row")
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
        var goods_name = obj["name"];
        if (obj["number"] > 1) {
            goods_name += "×" + obj["number"];
        }

        $("<div>")
            .html(core.text2html.parseHtml(goods_name))
            .appendTo(cell);
        cell.appendTo(row);

        // price
        var price = obj["price"] + obj["unit"];
        $("<td>")
            .text(price)
            .appendTo(row);

        // desc
        $("<td>")
            .html(core.text2html.parseHtml(obj["desc"]))
            .appendTo(row);

        row.appendTo(container);
	}

	this.onClick(".goods-row", this.onLook);
}


/******************************************
 *
 * Goods Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyGoods = function(el) {
	BaseController.call(this, el);

	this.goods = null;
}

MudderyGoods.prototype = prototype(BaseController.prototype);
MudderyGoods.prototype.constructor = MudderyGoods;

/*
 * Bind events.
 */
MudderyGoods.prototype.bindEvents = function() {
	this.onClick(".button-buy", this.onBuy);
	this.onClick(".button-close", this.onClose);
	this.onClick(".button-cancel", this.onClose);
}

 /*
 * Event when clicks the close button.
 */
MudderyGoods.prototype.onClose = function(element) {
	// close this window
    mud.main_game_window.popWindow(this);
}

/*
 * Event when clicks the buy button.
 */
MudderyGoods.prototype.onBuy = function(element) {
    if (this.goods) {
        core.service.buyGoods(this.goods["dbref"]);
    }

    // close this window
    mud.main_game_window.popWindow(this);
}

/*
 * Reset the goods
 */
MudderyGoods.prototype.reset = function() {
    this.select(".goods-name").empty();
    this.select(".goods-number_mark").hide();
    this.select(".goods-number").empty().hide();

    this.select(".goods-div-icon").hide();
    this.select(".goods_price").empty();
    this.select(".goods_unit").empty();

    // set desc
    this.select(".goods_desc").html(core.text2html.parseHtml(desc));
}

/*
 * Show goods to the player.
 */
MudderyGoods.prototype.setGoods = function(goods) {
    this.goods = goods;

    // add name
    this.select(".goods-name").html(core.text2html.parseHtml(goods["name"]));

    // set number
    if (goods["number"] > 1) {
        this.select(".goods-number-mark").show();
        this.select(".goods-number").text(goods["number"]);
    }

    // add icon
    if (goods["icon"]) {
        var url = settings.resource_url + goods["icon"];
        this.select(".goods-img-icon").attr("src", url);
        this.select(".goods-div-icon").show();
    }

    // set price
    this.select(".goods-price").text(goods["price"]);
    this.select(".goods-unit").text(goods["unit"]);

    // set desc
    this.select(".goods-desc").html(core.text2html.parseHtml(goods["desc"]));
}