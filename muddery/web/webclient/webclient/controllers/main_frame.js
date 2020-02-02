
/*
 * Derive from the base class.
 */
MudderyMainFrame = function(el) {
	BaseController.call(this, el);

	this.first_connection = true;
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
    this.popupMessage(core.trans("Alert"), message);
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
 * Show get objects messages.
 */
MudderyMainFrame.prototype.showGetObjects = function(objects) {
	// show accepted objects
	try {
		var first = true;
		for (var i = 0; i < objects.length; i++) {
		    if (!objects[i].reject) {
                if (first) {
                    mud.message_window.displayMessage(core.trans("You got:"));
                    first = false;
                }
                mud.message_window.displayMessage(objects[i]["name"] + ": " + objects[i]["number"]);
            }
		}
	}
	catch(error) {
		console.error(error.message);
	}

	// show rejected objects
	/*
	try {
		var first = true;
		for (var i = 0; i < objects.length; i++) {
		    if (objects[i].reject) {
                if (first) {
                    mud.message_window.displayMessage(core.trans("You can not get:"));
                    first = false;
                }
                mud.message_window.displayMessage(objects[i]["name"] + ": " + objects[i]["reject"]);
            }
		}
	}
	catch(error) {
		console.error(error.message);
	}
	*/

    mud.popup_get_objects.setObjects(objects);
    mud.popup_get_objects.show();
}
   
/*
 * Show the combat window. 
 */
MudderyMainFrame.prototype.showCombat = function(combat) {
	this.pushWindow(mud.combat_window);
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
	mud.main_title_bar.setStatus(status);
	mud.char_data_window.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
MudderyMainFrame.prototype.setCombatStatus = function(status) {
	mud.main_title_bar.setStatus(status);
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
	if (self.first_connection) {
	    self.first_connection = false;
	    mud.login_window.checkAutoLogin();
	}
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
	self.popupMessage(core.trans("Error"), core.trans("The client connection was closed cleanly."));
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

	mud.select_char_window.clear();
	
	//reconnect, show the connection screen
	Evennia.connect();
}

/*
 * Event when the player puppets a character.
 */
MudderyMainFrame.prototype.onPuppet = function(data) {
    core.data_handler.character_dbref = data["dbref"];
    core.data_handler.character_name = data["name"];

    mud.main_title_bar.setInfo(data["name"], data["icon"]);
    mud.char_data_window.setInfo(data["name"], data["icon"]);
    mud.combat_window.setInfo(data["name"], data["icon"]);
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
	this.onClick(".popup-buttons", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupMessage.prototype.onClose = function(element) {
    this.buttons = [];
    this.el.hide();
    this.select(".header-text").empty();
	this.select(".popup-body").empty();
	this.select(".popup-buttons").empty();
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

    var container = this.select(".popup-buttons");
	for (var i = 0; i < buttons.length; i++) {
		var name = core.text2html.parseHtml(buttons[i]["name"]);

		$("<button>").attr("type", "button")
		    .addClass("popup-button button-short")
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
	this.select(".header-text").html(core.text2html.parseHtml(obj["name"]));

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
		    .addClass("popup-button button-short")
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
MudderyPopupGetObjects.prototype.setObjects = function(objects) {
    var object_list = this.select(".popup-body");

    for (var i = 0; i < objects.length; i++) {
        var obj = objects[i];

        if (obj.reject) {
            continue;
        }

        var item = $("<p>")
            .appendTo(object_list);

        if (obj["icon"]) {
            $("<img>")
                .addClass("obj-icon")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(item);
        }

        $("<span>")
            .addClass("name")
            .text(obj["name"])
            .appendTo(item);

        if (obj["number"] != 1) {
            $("<span>")
                .addClass("number")
                .html("&times;" + obj["number"])
                .appendTo(item);
        }
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
            .addClass("popup-button button-next button-short")
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
            .addClass("popup-button button-short")
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
    this.onClick(".login-auto-login", this.onClickAutoLogin);
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
MudderyLogin.prototype.onClickAutoLogin = function(element) {
    this.select(".checkbox-auto-login").toggleClass("checked");
    var auto_login = this.select(".checkbox-auto-login").hasClass("checked");

    if (!auto_login) {
        this.removeAutoLogin();
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
    this.select(".checkbox-auto-login").removeClass("checked");
}

/*
 * Set the game's name.
 */
MudderyLogin.prototype.setGameName = function(name) {
    this.select(".title-text").html(core.text2html.parseHtml(name));
}

/*
 * Set welcome messages.
 */
MudderyLogin.prototype.setConnScreen = function(conn_screen) {
    this.select(".login-welcome").html(core.text2html.parseHtml(conn_screen));
}

/*
 * Set values.
 */
MudderyLogin.prototype.setValues = function(playername, password, auto_login) {
    this.select(".login-name").val(playername);
    this.select(".login-password").val(password);
    if (auto_login) {
        this.select(".checkbox-auto-login").addClass("checked");
    }
    else {
        this.select(".checkbox-auto-login").removeClass("checked");
    }
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
        var name = localStorage.login_name;
        var password = localStorage.login_password;

        this.setValues(name, password, true);
	    core.service.login(name, password);
    }
}

/*
 * On user login.
 */
MudderyLogin.prototype.onLogin = function() {
    var auto_login = this.select(".checkbox-auto-login").hasClass("checked");

    if (auto_login) {
        var name = this.select(".login-name").val();
        var password = this.select(".login-password").val();

        // Save the name and password.
        localStorage.login_name = name;
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

    this.max_number = 0;
    this.characters = [];
}

MudderySelectChar.prototype = prototype(BaseController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick(".character-list", ".character-item", this.onSelectCharacter);
    this.onClick(".character-list", ".button-delete", this.onDeleteCharacter);

    this.onClick(".button-new", this.onNewCharacter);
    this.onClick(".button-password", this.onPassword);
    this.onClick(".button-logout", this.onLogout);
}


/*
 * Reset the controller.
 */
MudderySelectChar.prototype.reset = function() {
}


/*
 * Clear the character list.
 */
MudderySelectChar.prototype.clear = function() {
    this.characters = [];
 	this.select(".character-list").empty();
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
MudderySelectChar.prototype.onDeleteCharacter = function(element, event) {
    event.stopPropagation();

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

	for (var i = characters.length - 1; i >= 0; i--) {
		var item = $("<div>")
		    .addClass("character-item")
			.data("index", i)
		    .prependTo(container);

		$("<span>")
		    .addClass("char-name")
			.text(characters[i]["name"])
			.appendTo(item);

		$("<button>")
		    .attr("type", "button")
		    .addClass("button-delete button-tiny-red")
			.data("index", i)
			.text(core.trans("Del"))
			.appendTo(item);
	}

	this.setNewCharButton();
}


/*
 * Set max character number.
 * If the character number is less than the max number, the player
 * can create new characters.
 */
MudderySelectChar.prototype.setMaxNumber = function(max_number) {
    this.max_number = max_number;
    this.setNewCharButton();
}


/*
 * Add a new character button if needs.
 */
MudderySelectChar.prototype.setNewCharButton = function() {
    if (this.characters.length >= this.max_number) {
        this.select(".character-list .button-new").hide();
    }
    else {
    	this.select(".character-list .button-new").show();
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

    core.service.changePassword(current, password, password_verify);
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

    this.onClick(this.onClickWindow);

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
 * Event when the window size changed.
 */
MudderyMainGame.prototype.onResize = function(element) {
    mud.main_game_window.resetSize();
}

/*
 * Event when clicks this window.
 */
MudderyMainGame.prototype.onClickWindow = function(element) {
    this.hidePopupMenus();
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
MudderyMainGame.prototype.onCharacter = function(element, event) {
    // Show the character menu.
    var hidden = this.select(".menu-character").hasClass("hidden");
    this.hidePopupMenus();
    if (hidden) {
        this.select(".menu-character").removeClass("hidden");
    }

    event.stopPropagation();
}

/*
 * Event when clicks the status button.
 */
MudderyMainGame.prototype.onStatus = function(element) {
    this.showWindow(mud.char_data_window);
}

/*
 * Event when clicks the inventory button.
 */
MudderyMainGame.prototype.onInventory = function(element) {
    this.showWindow(mud.inventory_window);
}

/*
 * Event when clicks the skills button.
 */
MudderyMainGame.prototype.onSkills = function(element) {
    this.showWindow(mud.skills_window);
}

/*
 * Event when clicks the character button.
 */
MudderyMainGame.prototype.onQuests = function(element) {
    this.showWindow(mud.quests_window);
}


/*
 * Event when clicks the system button.
 */
MudderyMainGame.prototype.onSystem = function(element) {
    // Show the character menu.
    var hidden = this.select(".menu-system").hasClass("hidden");
    this.hidePopupMenus();
    if (hidden) {
        this.select(".menu-system").removeClass("hidden");
    }

    event.stopPropagation();
}

/*
 * Event when clicks the logout button.
 */
MudderyMainGame.prototype.onLogout = function(element) {
    core.service.logout();
    Evennia.reconnect();
    mud.main_frame.showLoginWindow();
}

/*
 * Event when clicks the unpuppet button.
 */
MudderyMainGame.prototype.onUnpuppet = function(element) {
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
        left: button_char.position().left + button_char.outerWidth(true) / 2 - menu_char.outerWidth(true) / 2,
        top: button_char.position().top - menu_char.outerHeight() + 5,
    }
    menu_char.css(pos_char);

    // System menu.
    var button_sys = this.select(".button-system");
    var menu_sys = this.select(".menu-system");
    var pos_sys = {
        left: button_sys.position().left + button_sys.outerWidth(true) / 2 - menu_sys.outerWidth(true) / 2,
        top: button_sys.position().top - menu_sys.outerHeight() + 5,
    }
    menu_sys.css(pos_sys);
}

/*
 * Hide all popup menus.
 */
MudderyMainGame.prototype.hidePopupMenus = function(element) {
    this.select(".tab-bar .popup-menu").addClass("hidden");
}


/*
 * Show shop window.
 */
MudderyMainGame.prototype.showShop = function(data) {
	mud.main_frame.doClosePopupBox();
	mud.shop_window.setShop(data);
	this.showWindow(mud.shop_window);
}


/*
 * Popup shop goods.
 */
MudderyMainGame.prototype.showGoods = function(dbref, name, number, icon, desc, price, unit) {
	this.doClosePopupBox();

	var component = $$.component.goods;
	component.setGoods(dbref, name, number, icon, desc, price, unit);
	component.show()
}

/******************************************
 *
 * Title Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyTitleBar = function(el) {
	BaseController.call(this, el);

	this.full_hp_width = this.select(".hp-bar").width();
}

MudderyTitleBar.prototype = prototype(BaseController.prototype);
MudderyTitleBar.prototype.constructor = MudderyTitleBar;


/*
 * Set character's basic information.
 */
MudderyTitleBar.prototype.setInfo = function(name, icon) {
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
MudderyTitleBar.prototype.setStatus = function(status) {
    if ("level" in status) {
	    this.select(".level")
	        .text(core.trans("Lv ") + status["level"]["value"])
	        .show();
	}
	else {
	    this.select(".level").hide();
	}

    /*
    if ("exp" in status && "max_exp" in status) {
        var exp_str = "";
        if (status["max_exp"]["value"] > 0) {
            exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
        }
        else {
            exp_str = "--/--";
        }
        this.select(".exp")
            .text("Exp " + exp_str)
            .show();
    }
    else {
        this.select(".exp").hide();
    }
    */

    if ("hp" in status && "max_hp" in status) {
        this.select(".hp-bar").width(this.full_hp_width * status["hp"]["value"] / status["max_hp"]["value"]);
		this.select(".hp-number").text(status["hp"]["value"] + "/" + status["max_hp"]["value"]);
		this.select(".hp").show();
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
    this.equipment_pos = {};

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
 * Set player character's information.
 */
MudderyCharData.prototype.setStatus = function(status) {
    this.select(".data-list>tr").remove();
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
 * Set available equipment positions.
 */
MudderyCharData.prototype.setEquipmentPos = function(equipment_pos) {
    this.equipment_pos = {};
    for (var i = 0; i < equipment_pos.length; i++) {
        this.equipment_pos[equipment_pos[i]["key"]] = equipment_pos[i];
    }

    for (var pos in this.equipment_pos) {
        var block = this.select(".equipments .equipment-" + pos.toLowerCase());
        block.find(".position-name")
            .text(this.equipment_pos[pos].name)
            .show();
        block.find(".icon").hide();
        block.find(".name").hide();
        block.show();
    }
}

/*
 * Set player's equipments.
 */
MudderyCharData.prototype.setEquipments = function(equipments) {
    for (var pos in this.equipment_pos) {
        var equip = equipments[pos];
        var icon_url = "";
        var name = "";

        var block = this.select(".equipments .equipment-" + pos.toLowerCase());
        if (equip) {
            block.find(".position-name").hide();

            if (equip["icon"]) {
                icon_url = settings.resource_url + equip["icon"];
            }
            if (equip["name"]) {
                name = core.text2html.parseHtml(equip["name"]);
            }

            if (icon_url) {
                block.find(".icon")
                    .attr("src", icon_url)
                    .show();
            }
            else {
                block.find(".icon").hide();
            }

            block.find(".name")
                .html(name)
                .show();
        }
        else {
            block.find(".icon").hide();
            block.find(".name").hide();
            block.find(".position-name").show();
        }
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
	this.item_selected = null;
	this.buttons = [];
}

MudderyInventory.prototype = prototype(BaseController.prototype);
MudderyInventory.prototype.constructor = MudderyInventory;

/*
 * Bind events.
 */
MudderyInventory.prototype.bindEvents = function() {
    $(window).bind("resize", this.onResize);

    this.onClick(".inventory-list", ".inventory-item", this.onSelect);
    this.onClick(".item-info", ".button", this.onCommand);
}

/*
 * Reset the item info window.
 */
MudderyInventory.prototype.reset = function() {
    this.select(".item-info").hide();
    this.item_selected = null;
}

/*
 * Event when clicks a command button.
 */
MudderyInventory.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
		    core.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
		}
		else {
		    var self = this;
			var buttons = [
            {
                "name": core.trans("Cancel")
            },
            {
                "name": core.trans("Confirm"),
                "callback": function(data) {
                    self.confirmCommand(data);
                },
                "data": index,
            }
        ];
        mud.main_frame.popupMessage(core.trans("Warning"),
                                    this.buttons[index]["confirm"],
                                    buttons);
		}
	}
}

/*
 * Confirm the command.
 */
MudderyInventory.prototype.confirmCommand = function(data) {
	var index = data;
    core.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
}

/*
 * Event when the window size changed.
 */
MudderyInventory.prototype.onResize = function(element) {
    mud.inventory_window.resetSize();
}

/*
 * Set inventory list's width.
 */
MudderyInventory.prototype.resetSize = function() {
    var items = this.select(".inventory-list").children();
    if (items.length == 0) {
        return;
    }

    var block_width = this.select(".inventory-block").width();
    var item_width = $(items).outerWidth(true);
    var list_width = Math.floor(block_width / item_width) * item_width + 1;
    this.select(".inventory-list").width(list_width);
}

/*
 * Event when clicks the object link.
 */
MudderyInventory.prototype.onSelect = function(element) {
    var index = $(element).data("index");
    if (index < this.inventory.length) {
        this.item_selected = this.inventory[index].dbref;
        core.service.look(this.item_selected, "inventory");
    }
}

/*
 * Set inventory's data.
 */
MudderyInventory.prototype.setInventory = function(inventory) {
    this.inventory = inventory;

    var container = this.select(".inventory-list");
    container.empty();

    var has_selected_item = false;
    for (var i = 0; i < inventory.length; i++) {
        var obj = inventory[i];
        var item = $("<div>")
            .addClass("inventory-item")
            .data("index", i)
            .appendTo(container);

        if (obj["icon"]) {
            // Add icon.
            $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(item);
        }
        else {
            // Use name.
            name = core.text2html.parseHtml(obj["name"]);
            item.html(name);
        }

        // Equipped
        if ("equipped" in obj && obj["equipped"]) {
            $("<div>")
                .addClass("equipped")
                .text(core.trans("EQ"))
                .appendTo(item);
        }

        // number
        if (obj["number"] != 1 || !obj["can_remove"]) {
            $("<div>")
                .addClass("number")
                .text(obj["number"])
                .appendTo(item);
        }

        if (obj["dbref"] == this.item_selected) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.service.look(this.item_selected, "inventory");
    }
    else {
        this.item_selected = null;
        this.select(".item-info").hide();
    }
}

/*
 * Show the object's information.
 */
MudderyInventory.prototype.showObject = function(obj) {
    this.select(".item-info .icon-image").attr("src", settings.resource_url + obj["icon"]);

    // Equipped
    if ("equipped" in obj && obj["equipped"]) {
        this.select(".item-info .equipped").text(core.trans("EQ"));
    }
    else {
        this.select(".item-info .equipped").text("");
    }

    // number
    if (obj["number"] != 1 || !obj["can_remove"]) {
        this.select(".item-info .number").text(obj["number"]);
    }
    else {
        this.select(".item-info .number").text("");
    }

    this.select(".item-info .name").html(core.text2html.parseHtml(obj["name"]));
    this.select(".item-info .desc").html(core.text2html.parseHtml(obj["desc"]));

    // buttons
    this.buttons = obj["cmds"];
    var container = this.select(".item-info-left .buttons");
    container.children().remove();
    for (var i = 0; i < obj.cmds.length; i++) {
        $("<div>")
            .addClass("button")
            .data("index", i)
            .text(obj.cmds[i].name)
            .appendTo(container);
    }

    this.select(".item-info").show();
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
    this.onClick(".skills-list", ".skill-item", this.onSelect);
    this.onClick(".skill-info", ".button", this.onCommand);
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onSelect = function(element) {
    var index = $(element).data("index");
    if (index < this.skills.length) {
        var dbref = this.skills[index].dbref;
        core.service.look(dbref, "skills");
    }
}

/*
 * Event when clicks a command button.
 */
MudderySkills.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
		    core.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
		}
	}
}

/*
 * Set skills' data.
 */
MudderySkills.prototype.setSkills = function(skills) {
    this.skills = skills;

    var container = this.select(".skills-list");
    container.empty();

    var has_selected_item = false;
    for (var i = 0; i < skills.length; i++) {
        var obj = skills[i];
        var item = $("<div>")
            .addClass("skill-item")
            .data("index", i)
            .appendTo(container);

        var icon = $("<div>")
            .addClass("icon")
            .appendTo(item);

        if (obj["icon"]) {
            // Add icon.
            $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(icon);
        }

        var info = $("<div>")
            .addClass("info")
            .appendTo(item);

        // Name
        $("<div>")
            .addClass("name")
            .html(core.text2html.parseHtml(obj["name"]))
            .appendTo(info);

        // passive
        if ("passive" in obj && obj["passive"]) {
            $("<div>")
                .addClass("passive")
                .text(core.trans("Passive"))
                .appendTo(info);
        }

        if (obj["dbref"] == this.item_selected) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.service.look(this.item_selected, "skills");
    }
    else {
        this.item_selected = null;
        this.select(".skill-info").hide();
    }
}

/*
 * Show the skill's information.
 */
MudderySkills.prototype.showSkill = function(skill) {
    this.select(".skill-info .icon-image").attr("src", settings.resource_url + skill["icon"]);
    this.select(".skill-info .name").html(core.text2html.parseHtml(skill["name"]));
    this.select(".skill-info .desc").html(core.text2html.parseHtml(skill["desc"]));

    if ("passive" in skill && skill["passive"]) {
        this.select(".skill-info .passive").text(core.trans("Passive"));
    }
    else {
        this.select(".skill-info .passive").text("");
    }

    // buttons
    this.buttons = skill["cmds"];
    var container = this.select(".skill-info-left .buttons");
    container.children().remove();
    for (var i = 0; i < skill["cmds"].length; i++) {
        $("<div>")
            .addClass("button")
            .data("index", i)
            .text(skill["cmds"][i].name)
            .appendTo(container);
    }

    this.select(".skill-info").show();
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
    this.onClick(".quests-list", ".quest-item", this.onSelect);
    this.onClick(".quest-info", ".button", this.onCommand);
}

/*
 * Event when clicks the quest link.
 */
MudderyQuests.prototype.onSelect = function(element) {
    var index = $(element).data("index");
    if (index < this.quests.length) {
        var dbref = this.quests[index].dbref;
        core.service.look(dbref, "quests");
    }
}

/*
 * Event when clicks a command button.
 */
MudderyQuests.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
		    core.service.sendCommandLink(this.buttons[index]["cmd"], this.buttons[index]["args"]);
		}
		else {
		    var self = this;
			var buttons = [
            {
                "name": core.trans("Cancel")
            },
            {
                "name": core.trans("Confirm"),
                "callback": function(data) {
                    self.confirmCommand(data);
                },
                "data": index,
            }
        ];
        mud.main_frame.popupMessage(core.trans("Warning"),
                                    this.buttons[index]["confirm"],
                                    buttons);
		}
	}
}

/*
 * Set the player's quests.
 */
MudderyQuests.prototype.setQuests = function(quests) {
    this.quests = quests;

    var container = this.select(".quests-list");
    container.empty();

    var has_selected_item = false;
    for (var i = 0; i < quests.length; i++) {
        var obj = quests[i];
        var item = $("<div>")
            .addClass("quest-item")
            .data("index", i)
            .appendTo(container);

        // Name
        $("<div>")
            .addClass("name")
            .html(core.text2html.parseHtml(obj["name"]))
            .appendTo(item);

        // objectives
        if (obj["objectives"].length > 0) {
            $("<div>")
                .addClass("objective-title")
                .text(core.trans("Tasks:"))
                .appendTo(item);

            var obj_list = $("<div>")
                .addClass("objective-list")
                .appendTo(item);

            for (var j = 0; j < obj["objectives"].length; j++) {
                var objective = obj["objectives"][j];
                var row = $("<p>")
                    .addClass("objective");

                if ("desc" in objective) {
                    row.text(objective["desc"]);
                }
                else {
                    row.text(objective["target"] + " " +
                             objective["object"] + " " +
                             objective["accomplished"] + "/" +
                             objective["total"]);
                }
                row.appendTo(obj_list);
            }
        }

        if (obj["dbref"] == this.item_selected) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.service.look(this.item_selected, "quests");
    }
    else {
        this.item_selected = null;
        this.select(".quest-info").hide();
    }
}


/*
 * Show the quest's information.
 */
MudderyQuests.prototype.showQuest = function(quest) {
    this.select(".quest-info .name").html(core.text2html.parseHtml(quest["name"]));
    this.select(".quest-info .desc").html(core.text2html.parseHtml(quest["desc"]));

    // objectives
    var obj_block = this.select(".quest-info .objective-block");
    obj_block.children().remove();

    if (quest["objectives"].length > 0) {
        $("<div>")
            .addClass("objective-title")
            .text(core.trans("Tasks:"))
            .appendTo(obj_block);

        var obj_list = $("<div>")
            .addClass("objective-list")
            .appendTo(obj_block);

        for (var j = 0; j < quest["objectives"].length; j++) {
            var objective = quest["objectives"][j];
            var row = $("<p>")
                .addClass("objective");

            if ("desc" in objective) {
                row.text(objective["desc"]);
            }
            else {
                row.text(objective["target"] + " " +
                         objective["object"] + " " +
                         objective["accomplished"] + "/" +
                         objective["total"]);
            }
            row.appendTo(obj_list);
        }
    }

    // buttons
    this.buttons = quest["cmds"];
    var container = this.select(".quest-info .buttons");
    container.children().remove();
    for (var i = 0; i < quest["cmds"].length; i++) {
        $("<div>")
            .addClass("button")
            .data("index", i)
            .text(quest["cmds"][i].name)
            .appendTo(container);
    }

    this.select(".quest-info").show();
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
	this.onClick(".scene-commands", ".object-button", this.onCommand);
	this.onClick(".scene-objects", ".object-button", this.onObject);
	this.onClick(".scene-npcs", ".object-button", this.onNPC);
	this.onClick(".scene-players", ".object-button", this.onPlayer);
	this.onClick(".scene-exits", ".exit-button", this.onExit);

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
    core.service.look(dbref, "scene");
}

/*
 * On look at an NPC.
 */
MudderyScene.prototype.onNPC = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["npcs"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.look(dbref, "scene");
}

/*
 * On look at an player.
 */
MudderyScene.prototype.onPlayer = function(element) {
    var index = $(element).data("index");
    var dbref = this.scene["players"][index]["dbref"];
    dbref = dbref.slice(1);
    core.service.look(dbref, "scene");
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
    this.select(".scene-name").html(room_name);

    // add room's desc
    this.select(".scene-desc").html(core.text2html.parseHtml(scene["desc"]));

    // set commands
    var commands = this.select(".scene-commands");
    if ("cmds" in scene && scene["cmds"].length > 0) {
        for (var i = 0; i < scene["cmds"].length; i++) {
            $("<div>")
                .addClass("object-button")
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
            $("<div>")
                .addClass("scene-button object-button")
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
            $("<div>")
                .addClass("scene-button object-button")
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
            $("<div>")
                .addClass("scene-button object-button")
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

            // If the center grid is empty, show room's name in the center grid.
            if (i == 4) {
                var name = "";
                if (room_name) {
                    name = core.text2html.parseHtml(room_name);
                }

                $("<div>")
                    .addClass("exit-center")
                    .text(name)
                    .appendTo(p);
            }
            else {
                p.html("&nbsp;");
            }
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

            $("<div>")
                .addClass("exit-button exit-" + exit["index"])
                .data("index", exit["index"])
                .text(name)
                .appendTo(p);
        }
    }

    this.drawExitPaths(exits);

    // set height
    var height = this.select(".exits-table").height();
    this.select(".exits-block").height(height);
}

/*
 * Draw exit paths.
 */
MudderyScene.prototype.drawExitPaths = function(exits) {
    // draw exit lines
    var svg = document.getElementById("exits-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var center_dom = this.select(".direction-4");
    var x1 = center_dom.position().left + center_dom.outerWidth(true) / 2;
    var y1 = center_dom.position().top + center_dom.outerHeight(true) / 2;
    for (var i = 0; i < exits.length; i++) {
        var exit_dom = this.select(".exit-" + i);
        var x2 = exit_dom.position().left + exit_dom.outerWidth(true) / 2;
        var y2 = exit_dom.position().top + exit_dom.outerHeight(true) / 2;
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

	var map_width = this.select("#map-svg").width();
	var map_height = this.select("#map-svg").height();

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
	    /*
	    if (origin_x < map_width - location["area"]["background"]["width"]) {
	        origin_x = map_width - location["area"]["background"]["width"];
	    }
	    if (origin_y < map_height - location["area"]["background"]["height"]) {
	        origin_y = map_height - location["area"]["background"]["height"];
	    }
	    if (origin_x > 0) {
	        origin_x = 0;
	    }
	    if (origin_y > 0) {
	        origin_y = 0;
	    }
	    */

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

    this.combat_result = new MudderyCombatResult($("#combat-window .combat-result"));
    this.combat_result.init();

	this.self_dbref = "";
	this.target = "";
	this.interval_id = null;
	this.timeout = 0;
	this.timeline = 0;
	this.combat_finished = true;
	this.skill_cd_time = {};

	this.full_hp_width = this.select(".hp-bar").width();
	this.character_hp_width = 0;
}

MudderyCombat.prototype = prototype(BaseController.prototype);
MudderyCombat.prototype.constructor = MudderyCombat;

/*
 * Bind events.
 */
MudderyCombat.prototype.bindEvents = function() {
    $(window).bind("resize", this.onResize);

	this.onClick(".skill-list", ".skill-button", this.onCombatSkill);
}

/*
 * Event when the window size changed.
 */
MudderyCombat.prototype.onResize = function(element) {
    mud.combat_window.resetSize();
}

/*
 * Set inventory list's width.
 */
MudderyCombat.prototype.resetSize = function() {
    var items = this.select(".skill-list").children();
    if (items.length == 0) {
        return;
    }

    var block_width = this.select(".tab-bar").width();
    var item_width = $(items).outerWidth(true);
    var list_width = Math.floor(block_width / item_width) * item_width + 1;
    this.select(".skill-list").width(list_width);
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
 * Reset the combat box.
 */
MudderyCombat.prototype.reset = function(skill_cd_time) {
	this.select(".desc").empty();
	this.select(".game-time").empty();

	// Remove characters that are not template.
	this.select(".characters").empty();

	// Remove combat messages.
	this.select(".message-list").empty();

	// Remove skill buttons that are not template.
	this.select(".buttons").empty();

	this.self_dbref = "";
	this.target = "";
	this.combat_finished = true;
	this.skill_cd_time = core.data_handler.skill_cd_time;
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}

	// Clear combat results.
	this.select(".combat-result").hide();
}

/*
 * Set character's basic information.
 */
MudderyCombat.prototype.setInfo = function(name, icon) {
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
	this.select(".desc").html(core.text2html.parseHtml(desc));

	// add timeout
	if (timeout > 0) {
		var current_time = new Date().getTime();
		this.timeout = timeout;
		this.timeline = current_time + timeout * 1000;

		this.select(".game-time").text(timeout);
		this.select(".timeout").show();
		this.interval_id = window.setInterval("mud.combat_window.refreshTimeout()", 1000);
	}
	else {
		this.select(".game-time").empty();
		this.select(".timeout").hide();
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

        var hp = $("<div>")
            .addClass("character-hp")
            .appendTo(item);

        $("<div>")
            .addClass("character-hp-bar")
            .appendTo(hp);

		if (character["icon"]) {
		    var div_icon = $("<div>")
		        .addClass("character-icon")
		        .appendTo(item);

		    $("<img>")
		        .addClass("icon-img")
			    .attr("src", settings.resource_url + character["icon"])
			    .appendTo(div_icon);
		}

        $("<div>")
            .addClass("character-name")
		    .text(character["name"])
		    .appendTo(item);

		if (this.self_dbref == dbref) {
		    this.select(".title-bar>.name").text(character["name"]);
		}

		if (character["team"] == self_team) {
			item.addClass("character teammate")
			   .css('top', top + teammate_number * line_height);
			teammate_number++;
		}
		else {
			item.addClass("character enemy")
			   .css('top', top + enemy_number * line_height);
			enemy_number++;

			if (!this.target) {
				// Set default target.
				this.target = character["dbref"];
			}
		}

		item.appendTo(this.select(".characters"));
	}

    this.character_hp_width = $(".character-hp").width();
	this.updateStatus(status);
}

/*
 * Set combat commands.
 */
MudderyCombat.prototype.setCommands = function(commands) {
	var container = this.select(".skill-list");
	container.empty();

    for (var i in commands) {
        var command = commands[i];

        var item = $("<div>")
            .addClass("skill-button")
            .attr("id", "cmd-" + command["key"])
            .data("key", command["key"])
            .data("cd", 0);

        if (command["icon"]) {
            var div_icon = $("<div>")
                .appendTo(item);

            $("<img>")
                .addClass("skill-icon")
                .attr("src", settings.resource_url + command["icon"])
                .appendTo(item);
        }

        $("<div>")
            .addClass("skill-name")
            .html(core.text2html.parseHtml(command["name"]))
            .appendTo(item);

        $("<div>")
            .addClass("cooldown")
            .appendTo(item);

        item.appendTo(container);
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
	var msg_wnd = this.select(".message-list");
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
		var hp_bar = "#combat-char-" + key.slice(1) + " .character-hp-bar";
		$(hp_bar).width(this.character_hp_width * status[key]["hp"] / status[key]["max_hp"]);

		if (this.self_dbref == key) {
		    this.select(".hp-bar").width(this.full_hp_width * status[key]["hp"] / status[key]["max_hp"]);
		    this.select(".hp-number").text(status[key]["hp"] + "/" + status[key]["max_hp"]);
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
	var self = this;
	this.select(".skill-list>.skill-button").each(function() {
        self.showButtonCD(this);
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
 * Close the combat window.
 */
MudderyCombat.prototype.leftCombat = function(data) {
	this.combat_finished = true;
	if (this.interval_id != null) {
		window.clearInterval(this.interval_id);
		this.interval_id = null;
	}
}

/*
 * The combat has finished.
 */
MudderyCombat.prototype.finishCombat = function(result) {
	this.combat_finished = true;
	if (this.interval_id != null) {
		window.clearInterval(this.interval_id);
		this.interval_id = null;
	}

    this.combat_result.reset();
	this.combat_result.setResult(result);
	this.combat_result.show();
}

/*
 * Finish a combat.
 */
MudderyCombat.prototype.isCombatFinished = function() {
    return this.combat_finished;
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
 * Combat Result Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyCombatResult = function(el) {
	BaseController.call(this, el);
}

MudderyCombatResult.prototype = prototype(BaseController.prototype);
MudderyCombatResult.prototype.constructor = MudderyCombatResult;

/*
 * Reset the combat result box.
 */
MudderyCombatResult.prototype.reset = function(skill_cd_time) {
	// Clear combat results.
    this.select(".result-header").empty();
    this.select(".result-exp-block").hide();
    this.select(".result-exp").empty();
    this.select(".result-accepted").hide();
    this.select(".result-accepted-list").empty();
    this.select(".result-rejected").hide();
    this.select(".result-rejected-list").empty();
}

/*
 * Bind events.
 */
MudderyCombatResult.prototype.bindEvents = function() {
	this.onClick(".button-ok", this.onClose);
}

/*
 * Event when clicks the close button.
 */
MudderyCombatResult.prototype.onClose = function(element) {
	// close popup box
    this.hide();
    mud.main_frame.popWindow(mud.combat_window);

    if (mud.popup_dialogue.hasDialogue()) {
        mud.popup_dialogue.show();
    }
}

/*
 * Set result data.
 */
MudderyCombatResult.prototype.setResult = function(result) {
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

	this.select(".header-text").text(header);

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
MudderyCombatResult.prototype.setGetExp = function(exp) {
	this.select(".result-exp").text(exp);
	this.select(".result-exp-block").show();
}

/*
 * Set the objects that the player get.
 */
MudderyCombatResult.prototype.setGetObjects = function(objects) {
    var accepted_block = this.select(".result-accepted");
    var accepted_list = this.select(".result-accepted-list");
    //var rejected_block = this.select(".result-rejected");
    //var rejected_list = this.select(".result-rejected-list");

    for (var i = 0; i < objects.length; i++) {
        var obj = objects[i];

        var item = $("<p>")

        if (obj["icon"]) {
            $("<img>")
                .addClass("obj-icon")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(item);
        }

        $("<span>")
            .addClass("name")
            .text(obj["name"])
            .appendTo(item);

        if (obj["number"] != 1) {
            $("<span>")
                .addClass("number")
                .html("&times;" + obj["number"])
                .appendTo(item);
        }

        if (!obj.reject) {
            accepted_list.append(item);
            accepted_block.show();
        }
        else {
            //rejected_list.append(item);
            //rejected_block.show();
        }
    }
}

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

	this.goods_detail = new MudderyGoodsDetail($("#popup-goods"));
	this.goods_detail.init();

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

    // click goods
    this.onClick(".goods-list", ".goods", this.onClickGoods);
}

/*
 * Event when clicks the close button.
 */
MudderyShop.prototype.onClose = function(element) {
	// close popup box
    mud.main_game_window.showWindow(mud.scene_window);
}

/*
 * Event when clicks goods.
 */
MudderyShop.prototype.onClickGoods = function(element) {
    var index = $(element).data("index");
    if (index < this.goods.length) {
        var goods = this.goods[index];
        this.goods_detail.reset();
        this.goods_detail.setGoods(goods);
        this.goods_detail.show();
    }
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
	this.select(".desc-content").html(core.text2html.parseHtml(desc));

	// set goods
	var container = this.select(".goods-list");
	for (var i in this.goods) {
		var obj = this.goods[i];

        var item = $("<div>")
            .addClass("goods")
            .data("index", i);

        // icon
        var icon_div = $("<div>")
            .addClass("goods-icon")
            .appendTo(item);

        if (obj["icon"]) {
            $("<img>")
                .addClass("icon-image")
                .attr("src", settings.resource_url + obj["icon"])
                .appendTo(icon_div);
        }

        // name
        var goods_name = core.text2html.parseHtml(obj["name"]);
        if (obj["number"] > 1) {
            goods_name += "&times;" + obj["number"];
        }

        $("<div>")
            .addClass("goods-name")
            .html(goods_name)
            .appendTo(item);

        // price
        var price = obj["price"] + obj["unit"];
        $("<div>")
            .addClass("goods-price")
            .text(price)
            .appendTo(item);

        item.appendTo(container);
	}
}


/******************************************
 *
 * Goods Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyGoodsDetail = function(el) {
	BaseController.call(this, el);

	this.goods = null;
}

MudderyGoodsDetail.prototype = prototype(BaseController.prototype);
MudderyGoodsDetail.prototype.constructor = MudderyGoodsDetail;

/*
 * Bind events.
 */
MudderyGoodsDetail.prototype.bindEvents = function() {
	this.onClick(".button-buy", this.onBuy);
	this.onClick(".button-close", this.onClose);
	this.onClick(".button-cancel", this.onClose);
}

 /*
 * Event when clicks the close button.
 */
MudderyGoodsDetail.prototype.onClose = function(element) {
	// close this window
    this.el.hide();
}

/*
 * Event when clicks the buy button.
 */
MudderyGoodsDetail.prototype.onBuy = function(element) {
    if (this.goods) {
        core.service.buyGoods(this.goods["dbref"]);
    }

    // close this window
    this.el.hide();
}

/*
 * Reset the goods
 */
MudderyGoodsDetail.prototype.reset = function() {
    this.select(".icon-img").hide();
    this.select(".header-text").empty();
    this.select(".goods_price").empty();
    this.select(".goods_desc").empty();
}

/*
 * Show goods to the player.
 */
MudderyGoodsDetail.prototype.setGoods = function(goods) {
    this.goods = goods;

    // icon
    if (goods["icon"]) {
        var url = settings.resource_url + goods["icon"];
        this.select(".icon-img")
            .attr("src", url)
            .show();
    }
    else {
        this.select(".icon-img").hide();
    }

    // name
    var goods_name = core.text2html.parseHtml(goods["name"]);
    if (goods["number"] > 1) {
        goods_name += "&times;" + goods["number"];
    }
    this.select(".header-text").html(goods["name"]);

    // set price
    this.select(".goods-price").text(goods["price"] + goods["unit"]);

    // set desc
    this.select(".goods-desc").html(core.text2html.parseHtml(goods["desc"]));
}