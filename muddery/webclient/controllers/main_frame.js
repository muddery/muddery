
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
MudderyMainFrame.prototype.popupAlert = function(header, content) {
	this.doClosePopupBox();

	mud.popup_alert.setMessage(header, content);
    mud.popup_alert.show();
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
 * Show the combat window. 
 */
MudderyMainFrame.prototype.showCombat = function(combat) {
	this.pushWindow(mud.combat_window);
}

/*
 * Cast a combat skill.
 */
MudderyMainFrame.prototype.setSkillCast = function(result) {
    if ("state" in result && core.data_handler.character_id in result["state"]) {
        this.setSkillStatus(result["state"][core.data_handler.character_id]);
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
			mud.scene_window.displayMessage(message);
        }

        if ("result" in result && result["result"]) {
            this.popupMessage(
                core.trans("Alert"),
                result["result"]
            );
		}
	}
	else {
		mud.combat_window.setSkillCast(result);
	}
}


/*
 * Set the exp the player get.
 */
MudderyMainFrame.prototype.showGetExp = function(exp) {
	// show exp
	mud.scene_window.displayMessage(core.trans("You got exp: ") + exp);
}

/*
 *  Close the popup box.
 */
MudderyMainFrame.prototype.doClosePopupBox = function() {
	$("#popup_container").hide();
	$("#popup_container .modal-dialog").hide();
}


/*
 *  Set the player's state.
 */
MudderyMainFrame.prototype.setState = function(state) {
    if ("level" in state) {
	    core.data_handler.character_level = state["level"]["value"];
	}
	mud.scene_window.setState(state);
	mud.char_data_window.setState(state);
}

/*
 *  Set the player's state in combat.
 */
MudderyMainFrame.prototype.setSkillState = function(state) {
	mud.scene_window.setSkillState(state);
    mud.char_data_window.setSkillState(state);
}

/*
 * The player has prepared the honour match.
 */
MudderyMainFrame.prototype.prepareMatch = function(data) {
    mud.popup_confirm_combat.setTime(data);
	mud.popup_confirm_combat.show();
}

/*
 * The player has rejected the honour match.
 */
MudderyMainFrame.prototype.matchRejected = function(character_id) {
	if (character_id != core.data_handler.character_id) {
		mud.popup_confirm_combat.opponentReject();
	}
}

/*
 Handle quest changes.
 */
MudderyMainFrame.prototype.handle_quests = function(data) {
    if ("accomplished" in data) {
        // show accomplished quests.
        var accomplished = data["accomplished"];
        for (var i = 0; i < accomplished.length; i++) {
            if (accomplished[i]["name"]) {
                var msg = core.trans("Quest {C%s{n's goals are accomplished.").replace("%s", accomplished[i]["name"]);
                mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
            }
        }
    }
}

/*
 Handle all kind of events.
 */
MudderyMainFrame.prototype.handle_events = function(data) {
    for (var i = 0; i < data.length; i++) {
        if ("ACTION_DIALOGUE" in data[i]) {
            var event = data[i]["ACTION_DIALOGUE"];
            mud.popup_dialogue.setDialogue(event);
            if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                mud.popup_dialogue.show();
            }
        }
        else if ("ACTION_ACCEPT_QUEST" in data[i]) {
            var quests = data[i]["ACTION_ACCEPT_QUEST"];
            for (var q = 0; q < quests.length; q++) {
                if (quests[q]["name"]) {
                    var msg = core.trans("Accepted quest {C%s{n.").replace("%s", quests[q]["name"]);
                    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
                }
            }
        }
        else if ("ACTION_ATTACK" in data[i]) {
            this.handle_attack(data[i]["ACTION_ATTACK"], false);
        }
        else if ("ACTION_SET_RELATION" in data[i]) {
            var relations = data[i]["ACTION_SET_RELATION"];
            for (var r = 0; r < relations.length; r++) {
                if (relations[r]["name"]) {
                    var msg = core.trans("The relationship with %s1 becomes %s2.")
                        .replace("%s1", relations[r]["name"])
                        .replace("%s2", relations[r]["value"]);
                    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
                }
            }
        }
        else if ("ACTION_ADD_RELATION" in data[i]) {
            var relations = data[i]["ACTION_ADD_RELATION"];
            for (var r = 0; r < relations.length; r++) {
                if (relations[r]["name"]) {
                    if (relations[r]["value"] >= 0) {
                        var msg = core.trans("The relationship with %s1 increased by %s2.")
                            .replace("%s1", relations[r]["name"])
                            .replace("%s2", relations[r]["value"]);
                    }
                    else {
                        var msg = core.trans("The relationship with %s1 decreased by %s2.")
                            .replace("%s1", relations[r]["name"])
                            .replace("%s2", -relations[r]["value"]);
                    }
                    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
                }
            }
        }
        else if ("ACTION_TURN_IN_QUEST" in data[i]) {
            var quests = data[i]["ACTION_TURN_IN_QUEST"];
            for (var q = 0; q < quests.length; q++) {
                if (quests[q]["name"]) {
                    var msg = core.trans("Turned in quest {C%s{n.").replace("%s", quests[q]["name"]);
                    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
                }
            }
        }
        else if ("ACTION_LEARN_SKILL" in data[i]) {
            var skills = data[i]["ACTION_LEARN_SKILL"];
            for (var s = 0; s < skills.length; s++) {
                if (skills[s]["name"]) {
                    var msg = core.trans("You learned skill {C%s{n.").replace("%s", skills[s]["name"]);
                    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
                }
            }
        }
        else if ("ACTION_GET_OBJECTS" in data[i]) {
            var get_objects = data[i]["ACTION_GET_OBJECTS"];
            if ("msg" in get_objects) {
                mud.scene_window.displayMessage(core.text2html.parseHtml(get_objects["msg"]));
            }
        }
        else if ("ACTION_MESSAGE" in data[i]) {
            var messages = data[i]["ACTION_MESSAGE"];
            for (var m = 0; m < messages.length; m++) {
                if (messages[m]) {
                    mud.scene_window.displayMessage(core.text2html.parseHtml(messages[m]));
                }
            }
        }
        else if ("ACTION_CLOSE_EVENT" in data[i]) {
            // pass
        }
        else {
            this.popupAlert(core.trans("Error"), "Unknown event: " + Object.keys(data[i])[0]);
        }
    }
}

/*
 Handle attack.
 */
MudderyMainFrame.prototype.handle_attack = function(data, initiative) {
    this.handle_combat(data);

    if ("target" in data && initiative) {
        var msg = core.trans("You are attacking {R%s{n!").replace("%s", data["target"]);
        mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
    }

    if ("from" in data && !initiative) {
        var msg = core.trans("{R%s{n is attacking you!").replace("%s", data["from"]);
        mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
    }
}

/*
 Handle honour combat.
 */
MudderyMainFrame.prototype.honour_combat = function(data) {
    this.handle_combat(data);

    mud.honour_window.leftCombatQueue();

    var msg = core.trans("The combat of honour between you and {R%s{n!").replace("%s", data["target"]);
    mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
}

/*
 Handle combat.
 */
MudderyMainFrame.prototype.handle_combat = function(data) {
    this.showCombat();

    var info = data["combat_info"];
    var states = data["combat_states"];
    var commands = data["combat_commands"];

    mud.combat_window.setCombat(info["desc"], info["timeout"], info["characters"], core.data_handler.character_id);
    mud.combat_window.updateStates(states);
    mud.combat_window.setCommands(commands);
}

//////////////////////////////////////////
//
// Functional Windows
//
//////////////////////////////////////////

/*
 * Notify an object has moved to the player's current place.
 */
MudderyMainFrame.prototype.objMovedIn = function(obj) {
	mud.scene_window.addObject(obj);
}

/*
 * Notify an object has moved out the player's current place.
 */
MudderyMainFrame.prototype.objMovedOut = function(obj) {
	// If the player is talking to it, close the dialog window.
	if (mud.popup_dialogue.visible()) {
		mud.popup_dialogue.onObjMovedOut(obj["id"]);
	}
        
	// If the player is looking to it, close the look window.
	if (mud.popup_object.visible()) {
		mud.popup_object.onObjMovedOut(obj["id"]);
	}

	// remove objects from scene
	mud.scene_window.removeObject(obj);
}

/*
 *  The player is in a combat queue.
 */
MudderyMainFrame.prototype.inCombatQueue = function() {
    mud.scene_window.inCombatQueue();
    mud.honour_window.inCombatQueue();

	core.data_handler.queue_waiting_begin = new Date().getTime();
	var refreshWaitingTime = function() {
        var current_time = new Date().getTime();
        var total_time = Math.floor((current_time - core.data_handler.queue_waiting_begin) / 1000);
        var time_string = core.utils.time_to_string(total_time);
        mud.scene_window.refreshWaitingTime(time_string);
        mud.honour_window.refreshWaitingTime(time_string);
    }
    refreshWaitingTime();
	core.data_handler.queue_interval_id = window.setInterval(refreshWaitingTime, 1000);
}

/*
 *  The player left combat queue.
 */
MudderyMainFrame.prototype.leftCombatQueue = function() {
    mud.scene_window.leftCombatQueue();
    mud.honour_window.leftCombatQueue();

    if (core.data_handler.queue_interval_id) {
        window.clearInterval(core.data_handler.queue_interval_id);
        core.data_handler.queue_interval_id = 0;
    }
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

	    // Get the game's first connection data.
	    core.command.firstConnect(function(code, data, msg) {
	        if (code == 0) {
                if ("game_name" in data) {
                    mud.login_window.setGameName(data["game_name"]);
                }

                if ("conn_screen" in data) {
                    mud.login_window.setConnScreen(data["conn_screen"]);
                }

                if ("min_honour_level" in data) {
                    mud.honour_window.setMinHonourLevel(data["min_honour_level"]);
                }

                if ("equipment_pos" in data) {
                    mud.char_data_window.setEquipmentPos(data["equipment_pos"]);
                }

                if ("max_char" in data) {
                    mud.select_char_window.setMaxNumber(data["max_char"]);
                }

                mud.login_window.checkAutoLogin();
            }
            else {
                self.popupAlert(core.trans("Error"), core.trans(msg));
            }
	    });
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
	self.popupAlert(core.trans("Error"), core.trans("The client connection was closed cleanly."));
}

/*
 * Event when the player logs out.
 */
MudderyMainFrame.prototype.onLogout = function(data) {
	this.puppet = false;
	
	// show unlogin UI
	this.showLoginWindow();

	mud.select_char_window.clear();
}

/*
 * Event when the player unpuppets a character.
 */
MudderyMainFrame.prototype.onUnpuppet = function() {
    if (!this.puppet) {
        return;
    }
	this.puppet = false;
	this.leftCombatQueue();
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
    this.puppet = true;
	this.gotoWindow(mud.game_window);
	mud.game_window.onScene();
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
 * Show the button that can input commands.
 */
MudderyMainFrame.prototype.showCommandButton = function(show) {
    if (show) {
        // show command button
        this.select(".tab-bar .block-button-command").removeClass("hidden");
    }
    else {
        this.select(".tab-bar .block-button-command").addClass("hidden");
    }
}

/*
 * Show the layout when players unlogin.
 */
MudderyMainFrame.prototype.showLoginWindow = function() {
	// show unlogin UI
	this.gotoWindow(mud.login_window);
	core.map_data.clearData();
}
    
/*
 * Show the layout when players logged in and going to select a character.
 */
MudderyMainFrame.prototype.showSelectChar = function() {
	core.map_data.clearData();
	this.gotoWindow(mud.select_char_window);
}


/*
 * Show the layout when players has not connected.
 */
MudderyMainFrame.prototype.showConnect = function() {
	this.hideTabs();
	
	$("#tab_connect").show();
	
	window_main.showContent("connect");
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
    this.clear();
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
    this.clear();

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


/*
 * Clear the dialogue.
 */
MudderyPopupMessage.prototype.clear = function() {
    this.select(".header-text").empty();
	this.select(".popup-body").empty();
	this.select(".popup-buttons").empty();
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
	var button = this.buttons[index];
	if ("cmd" in button && "args" in button) {
	    var command = button["cmd"];
		core.command.sendCommand(button["cmd"], button["args"], function(code, data, msg) {
            if (code != 0) {
                mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
            }
            else if (code == ERR.died) {
                mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
            }
            else {
                if (command == "loot") {
                    mud.popup_get_objects.setObjects(data["objects"]);
                    mud.popup_get_objects.show();

                    if ("quests" in data) {
                        mud.main_frame.handle_quests(data["quests"]);
                    }
                }
                else if (command == "unlock_exit") {
                    mud.popup_object.setObject(data["exit"]);
                    mud.popup_object.show();
                }
                else if (command == "traverse") {
                    if (data["traversed"]) {
                        core.map_data.setCurrentLocation(data["location"]);
                        mud.scene_window.setSurroundings(data["look_around"]);

                        if ("quests" in data) {
                            mud.main_frame.handle_quests(data["quests"]);
                        }
                        if ("events" in data) {
                            mud.main_frame.handle_events(data["events"]);
                        }
                    }
                    else {
                        mud.popup_object.setObject(data["exit"]);
                        mud.popup_object.show();
                    }
                }
                else if (command == "talk") {
                    mud.popup_dialogue.setDialogue(data);
                    if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                        mud.popup_dialogue.show();
                    }
                }
                else if (command == "attack") {
                    mud.main_frame.handle_attack(data["attack"], true);
                }
                else if (command == "shopping") {
                    mud.game_window.showShop(data);
                }
                else if (command == "use") {
                    if (data) {
                        mud.main_frame.popupAlert(core.trans("Alert"), data["msg"]);

                        if ("state" in data) {
                            mud.main_frame.setState(data["state"]);
                        }
                    }
                    else {
                        mud.main_frame.popupAlert(core.trans("Alert"), core.trans("No effect."));
                    }
                }
            }
		});
	}

	this.onClose();
}

/*
 * Event when an object moved out from the current place.
 */
MudderyPopupObject.prototype.onObjMovedOut = function(odj_id) {
    if (!this.object) {
        return;
    }

    if (odj_id == this.object["id"]) {
		this.onClose();
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

    if (!objects || !objects.length) {
        $("<p>")
            .append(core.trans("You get nothing."))
            .appendTo(object_list);
    }

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
            .html(core.text2html.parseHtml(obj["name"]))
            .appendTo(item);

        if (obj["number"] != 1) {
            $("<span>")
                .addClass("number")
                .html("&times;" + obj["number"])
                .appendTo(item);
        }
    }

    for (var i = 0; i < objects.length; i++) {
        var obj = objects[i];

        if (!obj.reject) {
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
            .addClass("reject")
            .html(obj["reject"])
            .appendTo(item);
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

    this.dialogues = [];
    this.d_index = 0;       // current dialogue's index
    this.s_index = 0;       // current sentence's index
	this.target = {};
}

MudderyPopupDialogue.prototype = prototype(BaseController.prototype);
MudderyPopupDialogue.prototype.constructor = MudderyPopupDialogue;

/*
 * Bind events.
 */
MudderyPopupDialogue.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
    this.onClick(".div-dialogue", ".select", this.onSelect);
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
 * Event when select a dialogue.
 */
MudderyPopupDialogue.prototype.onSelect = function(element) {
    this.d_index = this.select(element).data("dialogue");
    this.gotoNext();
}

/*
 * Event when clicks the next button.
 */
MudderyPopupDialogue.prototype.onNext = function(element) {
    this.gotoNext();
}

/*
 * Goto next sentence.
 */
MudderyPopupDialogue.prototype.gotoNext = function() {
    var dlg = this.dialogues[this.d_index];
    if (this.s_index + 1 < dlg.sentences.length) {
        // Display next sentence.
        this.s_index += 1;
        this.displaySentence(dlg.sentences[this.s_index]);
    }
    else {
		core.command.finishDialogue(dlg.key, this.target.id? this.target.id: "", function(code, data, msg) {
		    if (code == 0) {
		        var dialogue = "dialogue" in data? data["dialogue"]: null;
                mud.popup_dialogue.setDialogue(dialogue);
                if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                    mud.popup_dialogue.show();
                }

                if ("events" in data) {
                    mud.main_frame.handle_events(data["events"]);
                }
		    }
		    else {
		        mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
		    }
		});
	}
}

/*
 * Event when objects moved out from the current place.
 */
MudderyPopupDialogue.prototype.onObjMovedOut = function(obj_id) {
    if (this.target && this.target.id == obj_id) {
        this.onClose();
        return;
    }
}

/*
 * Set dialogue's data.
 */
MudderyPopupDialogue.prototype.setDialogue = function(dialogue) {
    this.d_index = 0;
    this.s_index = 0;

    if (!dialogue || dialogue.dialogues.length == 0) {
        this.dialogues = [];
        this.target = {};
        this.onClose();
        return;
    }

    this.target = dialogue.target? dialogue.target: {};

    this.dialogues = dialogue.dialogues;
    var escapes = core.data_handler.getEscapes();
    for (var i = 0; i < this.dialogues.length; i++) {
        this.parseDialogue(this.dialogues[i], this.target, escapes);
    }

    /*
	if (sentences[0]["can_close"]) {
		this.select(".button-close").show();
	}
	else {
		this.select(".button-close").hide();
	}
    */

    // set content
    if (this.dialogues.length == 1 && this.dialogues[0].sentences.length > 0) {
        // Only one dialogue.
        this.displaySentence(this.dialogues[0].sentences[0]);
    }
    else {
        this.chooseDialogue(this.dialogues);
    }
}

MudderyPopupDialogue.prototype.displaySentence = function(sentence) {
    // set speaker and icon
    this.select(".header-text").html(sentence.speaker);

    // add icon
    if (sentence.icon) {
        this.select(".img-icon").attr("src", sentence.icon);
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

    container.html(sentence.content);

    $("<button>").attr("type", "button")
        .addClass("popup-button button-next button-short")
        .html(core.trans("Next"))
        .appendTo(footer);
}

MudderyPopupDialogue.prototype.chooseDialogue = function(dialogues) {
    // set speaker and icon
    for (var i = 0; i < dialogues.length; i++) {
        if (dialogues[i].sentences.length > 0) {
            var sentence = dialogues[i].sentences[0];
            this.select(".header-text").html(sentence.speaker);

            // add icon
            if (sentence.icon) {
                this.select(".img-icon").attr("src", sentence.icon);
                this.select(".div-icon").show();
            }
            else {
                this.select(".div-icon").hide();
            }

            break;
        }
    }

	// set contents and buttons
    var container = this.select(".div-dialogue");
    container.empty();
    var footer = this.select(".popup-footer");
    footer.empty();

    for (var i = 0; i < this.dialogues.length; i++) {
        // Select one dialogue.
        $("<p>")
            .addClass("select")
            .data("dialogue", i)
            .html(this.dialogues[i].sentences[0].content)
            .appendTo(container);
    }

    $("<button>").attr("type", "button")
        .addClass("popup-button button-short")
        .html(core.trans("Select One"))
        .appendTo(footer);
}

MudderyPopupDialogue.prototype.parseDialogue = function(dialogue, target, escapes) {
    // parse sentences
    var lines = dialogue.content.split(/[(\r\n)\r\n]+/);
    var sentences = [];

    var speaker = "";
    var icon = "";
    var content = "";

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var new_line = false;

        if (line.length > 1 && line[0] == "[") {
            var end = line.indexOf("]");
            if (end > 0) {
                new_line = true;
                speaker = "";
                icon = "";

                // get speaker
                speaker = line.substring(1, end);
                line = line.substring(end + 1);

                // get icon
                if (line[0] == "[") {
                    end = line.indexOf("]");
                    if (end > 0) {
                        icon = line.substring(1, end);
                        line = line.substring(end + 1);
                    }
                }
            }
        }

        if (new_line) {
            // parse icon
            if (icon) {
                icon = settings.resource_url + icon;
            }
            else {
                // use speaker's icon
                if (speaker == "%p") {
                    icon = settings.resource_url + core.data_handler.character_icon;
                }
                else if (speaker == "%t") {
                    if (target.icon) {
                        icon = settings.resource_url + target.icon;
                    }
                    else {
                        icon = "";
                    }
                }
            }

            // parse speaker
            // %p is the player
            // %t is the target
            if (speaker == "%p") {
                speaker = core.data_handler.character_name;
            }
            else if (speaker == "%t") {
                if (target.name) {
                    speaker = target.name;
                }
                else {
                    speaker = "";
                }
            }
            else if (speaker) {
                speaker = core.text2html.parseHtml(speaker);
            }
            else {
                speaker = "&nbsp;";
            }

            line = core.text2html.parseHtml(line);
            line = core.text_escape.parse(line, escapes);
            sentences.push({
                speaker: speaker,
                icon: icon,
                content: line,
            });
        }
        else if (sentences.length > 0) {
            // Add to the last sentence.
            line = core.text2html.parseHtml(line);
            line = core.text_escape.parse(line, escapes);
            sentences[sentences.length - 1].content += "<br>" + line;
        }
    }

    dialogue.sentences = sentences;
}

MudderyPopupDialogue.prototype.hasDialogue = function() {
    return (this.dialogues && this.dialogues.length > 0);
}


/******************************************
 *
 * Popup Confirm Combat Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupConfirmCombat = function(el) {
	BaseController.call(this, el);

    this.prepare_time = 0;
    this.interval_id = null;
    this.confirmed = false;
}

MudderyPopupConfirmCombat.prototype = prototype(BaseController.prototype);
MudderyPopupConfirmCombat.prototype.constructor = MudderyPopupConfirmCombat;

/*
 * Bind events.
 */
MudderyPopupConfirmCombat.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onRejectCombat);
    this.onClick(".button-cancel", this.onRejectCombat);
    this.onClick(".button-ok", this.onConfirmCombat);
    this.onClick(".button-finish", this.onFinish);
}

/*
 * Init the dialog with confirm time..
 */
MudderyPopupConfirmCombat.prototype.setTime = function(time) {
	this.confirmed = false;
	this.select(".confirm-body").text(core.trans("Found an opponent."));

	this.prepare_time = new Date().getTime() + time * 1000;
	this.select(".confirm-time").text(parseInt(time - 1) + core.trans(" seconds to confirm."));

    this.select(".button-cancel").show();
    this.select(".button-ok").show();
    this.select(".button-finish").hide();

	this.interval_id = window.setInterval(function(){
	    mud.popup_confirm_combat.refreshPrepareTime();
	}, 1000);
}

/*
 * Event when clicks the confirm button.
 */
MudderyPopupConfirmCombat.prototype.onConfirmCombat = function(element) {
	if (this.confirmed) {
		return;
	}
	this.confirmed = true;

	core.command.confirmCombat(function(code, data, msg) {
        if (code == 0) {
            mud.popup_confirm_combat.combatConfirmed();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Combat confirmed.
 */
MudderyPopupConfirmCombat.prototype.combatConfirmed = function() {
    this.select(".confirm-body").text(core.trans("Waiting the opponent to confirm."));
    this.select(".button-cancel").hide();
    this.select(".button-ok").hide();
}

/*
 * Event when clicks the close button.
 */
MudderyPopupConfirmCombat.prototype.onRejectCombat = function(element) {
	if (this.confirmed) {
		return;
	}

    if (this.interval_id != null) {
        window.clearInterval(this.interval_id);
        this.interval_id = 0;
    }

    this.el.hide();
	core.command.rejectCombat(function(code, data, msg) {
        if (code == 0) {
	        mud.honour_window.leftCombatQueue();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks the OK button when the opponent rejected the combat.
 */
MudderyPopupConfirmCombat.prototype.onFinish = function(element) {
    this.el.hide();
}

/*
 * Refresh the time.
 */
MudderyPopupConfirmCombat.prototype.refreshPrepareTime = function() {
    var current_time = new Date().getTime();
    var remain_time = Math.floor((this.prepare_time - current_time) / 1000);
    if (remain_time < 0) {
        remain_time = 0;
    }
    var text = core.trans(" seconds to confirm.");
    this.select(".confirm-time").text(parseInt(remain_time) + text);

    if (remain_time <= 0) {
        if (this.interval_id != null) {
            window.clearInterval(this.interval_id);
            this.interval_id = 0;
        }

        if (this.confirmed) {
            // Waiting the opponent to confirm.
        }
        else {
            // Reject the combat automatically.
            this.onRejectCombat();
        }
    }
}

/*
 * The opponent rejected the combat.
 */
MudderyPopupConfirmCombat.prototype.opponentReject = function() {
    if (this.interval_id) {
		window.clearInterval(this.interval_id);
		this.interval_id = 0;
	}

	this.confirmed = false;

    this.select(".confirm-body").text(core.trans("Your opponent has rejected the combat. You are back to the waiting queue."));
	this.select(".confirm-time").text("");

    this.select(".button-cancel").hide();
    this.select(".button-ok").hide();
    this.select(".button-finish").show();
}

/******************************************
 *
 * Popup Input Command Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyPopupInputCommand = function(el) {
	BaseController.call(this, el);
}

MudderyPopupInputCommand.prototype = prototype(BaseController.prototype);
MudderyPopupInputCommand.prototype.constructor = MudderyPopupInputCommand;

/*
 * Bind events.
 */
MudderyPopupInputCommand.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
    this.onClick(".button-send", this.onSend);
}

/*
 * Event when clicks the close button.
 */
MudderyPopupInputCommand.prototype.onClose = function(element) {
    this.el.hide();
    this.select(".command-text").empty();
}

/*
 * Event when clicks the next button.
 */
MudderyPopupInputCommand.prototype.onSend = function(element) {
	var command = this.select(".command-text").val();
	this.select(".command-text").val("");

	core.command.sendRawCommand(command);
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
    var username = this.select(".reg-name").val();
    var password = this.select(".reg-password").val();
    var password_verify = this.select(".reg-password-verify").val();

    if (password != password_verify) {
        mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
        return;
    }

    core.command.register(username, password, true, function(code, data, msg) {
        if (code == 0) {
            mud.login_window.loginSuccess();
        }
        else if (code === ERR.missing_args || code === ERR.invalid_input) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Incorrect username or password."));
        }
        else if (code === ERR.account_not_available) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("This username is not available."));
        }
        else if (code === ERR.password_too_simple) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Your password is too simple."));
        }
        else if (code === ERR.no_authentication) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Incorrect username or password."));
        }
        else if (code === ERR.no_permission) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Your account have been banned."));
        }
        else {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Can not create this account."));
        }
    });
    this.clearValues();
}

/*
 * Event on click the login button.
 */
MudderyLogin.prototype.onClickLogin = function(element) {
    var name = this.select(".login-name").val();
    var password = this.select(".login-password").val();

    core.command.login(name, password, function(code, data, msg) {
        if (code == 0) {
            mud.login_window.loginSuccess();
        }
        else if (code === ERR.no_authentication || code === ERR.missing_args || code === ERR.invalid_input) {
            mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Incorrect username or password."));
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
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
MudderyLogin.prototype.setValues = function(username, password, auto_login) {
    this.select(".login-name").val(username);
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
	    core.command.login(name, password);
    }
}

/*
 * On user login.
 */
MudderyLogin.prototype.loginSuccess = function() {
    // Save the password.
    var auto_login = this.select(".checkbox-auto-login").hasClass("checked");
    if (auto_login) {
        var name = this.select(".login-name").val();
        var password = this.select(".login-password").val();

        // Save the name and password.
        localStorage.login_name = name;
        localStorage.login_password = password;
        localStorage.is_auto_login = "1";
    }

    mud.main_frame.showSelectChar();
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
    core.command.queryAllCharacters(function(code, data, msg) {
        if (code == 0) {
            if ("char_all" in data) {
                mud.select_char_window.setCharacters(data["char_all"]);
            }
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
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
    core.command.logout();
    mud.main_frame.showLoginWindow();
}

/*
 * On select a character.
 */
MudderySelectChar.prototype.onSelectCharacter = function(element) {
    var index = this.select(element).data("index");
    core.command.puppetCharacter(this.characters[index]["id"], function(code, data, msg) {
        if (code == 0) {
            core.data_handler.character_id = data["id"];
            core.data_handler.character_icon = data["icon"];

            var name = data["name"];
            if (data["is_staff"]) {
                name += "[" + core.trans("ADMIN") + "]";
            }
            core.data_handler.character_name = name;

            mud.scene_window.clear();
            mud.scene_window.setInfo(name, data["icon"]);
            mud.char_data_window.setInfo(name, data["icon"]);
            mud.combat_window.setInfo(name, data["icon"]);

            mud.main_frame.setState(data["state"]);
            mud.conversation_window.setChannels(data["channels"]);

            if ("allow_commands" in data && data["allow_commands"]) {
                // show command button
                mud.main_frame.showCommandButton(true);
            }
            else {
                mud.main_frame.showCommandButton(false);
            }

            if ("reveal_maps" in data) {
                core.map_data.revealMaps(data["reveal_maps"]);
            }

            if ("location" in data) {
                core.map_data.setCurrentLocation(data["location"]);
            }

            if ("look_around" in data) {
                mud.scene_window.setSurroundings(data["look_around"]);
            }

            mud.main_frame.showPuppet();

            if ("last_combat" in data) {
                mud.main_frame.handle_combat(data["last_combat"]);
            }

            if ("last_dialogue" in data) {
                mud.popup_dialogue.setDialogue(data["last_dialogue"]);
                if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                    mud.popup_dialogue.show();
                }
            }
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
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
	        "data": this.characters[index]["id"]
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
	var obj_id = data;
    core.command.deleteCharacter(obj_id, function(code, data, msg) {
        if (code == 0) {
            mud.select_char_window.reset();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Set playable characters.
 */
MudderySelectChar.prototype.setCharacters = function(characters) {
    this.characters = characters;

	var container = this.select(".character-list");
	container.empty();

    if (characters.length > 0) {
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
    }
    else {
        $("<div>")
            .addClass("create-character")
            .text(core.trans("Please create a character."))
            .appendTo(container);
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
	core.command.createCharacter(char_name, function(code, data, msg) {
	    if (code == 0) {
            // close popup windows
            mud.new_char_window.reset();
            mud.select_char_window.reset();
            mud.main_frame.popWindow(mud.new_char_window);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
        }
	});
}

/*
 * Reset the element.
 */
MudderyNewChar.prototype.reset = function() {
    this.select(".new-char-name").val("");
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

    if (password != password_verify) {
        mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
        return;
    }

    core.command.changePassword(current, password, function() {
        mud.main_frame.popWindow(mud.password_window);
        mud.main_frame.popupMessage(core.trans("Alert"), core.trans("Password changed."));
    });

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
MudderyGame = function(el) {
	BaseController.call(this, el);
	this.current_window = null;
}

MudderyGame.prototype = prototype(BaseController.prototype);
MudderyGame.prototype.constructor = MudderyGame;

/*
 * Bind events.
 */
MudderyGame.prototype.bindEvents = function() {
    $(window).bind("resize", this.onResize);

    this.onClick(this.onClickWindow);

    this.onClick(".button-scene", this.onScene);
	this.onClick(".button-map", this.onMap);

    this.onClick(".button-character", this.onCharacter);
    this.onClick(".button-state", this.onState);
    this.onClick(".button-inventory", this.onInventory);
    this.onClick(".button-skills", this.onSkills);
    this.onClick(".button-quests", this.onQuests);
    this.onClick(".button-honour", this.onHonour);

    this.onClick(".button-system", this.onSystem);
    this.onClick(".button-logout", this.onLogout);
    this.onClick(".button-unpuppet", this.onUnpuppet);
    this.onClick(".button-input-command", this.onInputCommand);
}

/*
 * Show the window.
 */
MudderyGame.prototype.show = function() {
	BaseController.prototype.show.call(this);

	if (this.current_window) {
	    this.current_window.show();
	}
}

/*
 * Show a window.
 */
MudderyGame.prototype.showWindow = function(win_controller) {
    this.current_window = win_controller;
    this.select(".contents>div").hide();
    win_controller.show();
}

/*
 * Event when the window size changed.
 */
MudderyGame.prototype.onResize = function(element) {
    mud.game_window.resetSize();
}

/*
 * Event when clicks this window.
 */
MudderyGame.prototype.onClickWindow = function(element) {
    this.hidePopupMenus();
}

/*
 * Event when clicks the scene button.
 */
MudderyGame.prototype.onScene = function(element) {
    this.showWindow(mud.scene_window);
}

/*
 * Event when clicks the map button.
 */
MudderyGame.prototype.onMap = function(element) {
    this.showWindow(mud.map_window);
}


/*
 * Event when clicks the character button.
 */
MudderyGame.prototype.onCharacter = function(element, event) {
    // Show the character menu.
    var hidden = this.select(".menu-character").hasClass("hidden");
    this.hidePopupMenus();
    if (hidden) {
        this.select(".menu-character").removeClass("hidden");
    }

    event.stopPropagation();
}

/*
 * Event when clicks the state button.
 */
MudderyGame.prototype.onState = function(element) {
    this.showWindow(mud.char_data_window);
}

/*
 * Event when clicks the inventory button.
 */
MudderyGame.prototype.onInventory = function(element) {
    this.showWindow(mud.inventory_window);
}

/*
 * Event when clicks the skills button.
 */
MudderyGame.prototype.onSkills = function(element) {
    this.showWindow(mud.skills_window);
}

/*
 * Event when clicks the quests button.
 */
MudderyGame.prototype.onQuests = function(element) {
    this.showWindow(mud.quests_window);
}


/*
 * Event when clicks the honour button.
 */
MudderyGame.prototype.onHonour = function(element) {
    this.showWindow(mud.honour_window);
}


/*
 * Event when clicks the system button.
 */
MudderyGame.prototype.onSystem = function(element, event) {
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
MudderyGame.prototype.onLogout = function(element) {
    core.command.logout();
    mud.main_frame.showLoginWindow();
}

/*
 * Event when clicks the unpuppet button.
 */
MudderyGame.prototype.onUnpuppet = function(element) {
	core.command.unpuppetCharacter();
	mud.main_frame.onUnpuppet();
}

/*
 * Event when clicks the input command button.
 */
MudderyGame.prototype.onInputCommand = function(element) {
	mud.main_frame.doClosePopupBox();

    mud.popup_input_command.show();
}

/*
 * Set popup menus position.
 */
MudderyGame.prototype.resetSize = function(element) {
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
MudderyGame.prototype.hidePopupMenus = function(element) {
    this.select(".tab-bar .popup-menu").addClass("hidden");
}


/*
 * Show shop window.
 */
MudderyGame.prototype.showShop = function(data) {
	mud.main_frame.doClosePopupBox();
	mud.shop_window.reset();
	this.showWindow(mud.shop_window);
	mud.shop_window.setShop(data);
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

    this.title_bar = new MudderyTitleBar(this.select(".title-bar"));
    this.title_bar.init();

    this.max_player = 10;
    this.path_color = "#666";
    this.path_width = "3";
	this.max_messages = 200;

	this.surroundings = null;
}

MudderyScene.prototype = prototype(BaseController.prototype);
MudderyScene.prototype.constructor = MudderyScene;

/*
 * Bind events.
 */
MudderyScene.prototype.bindEvents = function() {
	this.onClick(".scene-commands", ".object-button", this.onCommand);
	this.onClick(".scene-objects", ".object-button.object", this.onObject);
	this.onClick(".scene-objects", ".object-button.npc", this.onNPC);
	this.onClick(".scene-players", ".object-button.player", this.onPlayer);
	this.onClick(".scene-exits", ".exit-button", this.onExit);
	this.onClick(".conversation-button", this.OnConversation);

    !function(caller, method) {
		$(window).on("resize", undefined, caller, function(event) {
    		method.call(event.data, event.currentTarget, event);
    	});
    }(this, this.onResize);
}

/*
 * Show the window.
 */
MudderyScene.prototype.show = function() {
	BaseController.prototype.show.call(this);

	var message_list = this.select(".message-list");
    message_list.stop(true);
    message_list.scrollTop(message_list[0].scrollHeight);
}

/*
 * On click a command.
 */
MudderyScene.prototype.onCommand = function(element) {
    var index = $(element).data("index");
    var cmd = this.surroundings["cmds"][index]["cmd_name"];
    var args = this.surroundings["cmds"][index]["cmd_args"];
    core.command.sendCommandLink(cmd, args);
}

/*
 * On look at an object.
 */
MudderyScene.prototype.onObject = function(element) {
    var index = $(element).data("index");

    var room_map = core.map_data.getCurrentRoomMap();
    var object_key = room_map["objects"][index]["key"];
    core.command.lookRoomObj(object_key, function(code, data, msg) {
        if (code == 0) {
            mud.popup_object.setObject(data);
            mud.popup_object.show();
        }
        else if (code == ERR.died) {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
        }
        else {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
        }
    });
}

/*
 * On look at an NPC.
 */
MudderyScene.prototype.onNPC = function(element) {
    var index = $(element).data("index");
    var obj_id = this.surroundings["npcs"][index]["id"];
    core.command.lookRoomChar(obj_id, function(code, data, msg) {
        if (code == 0) {
            mud.popup_object.setObject(data);
            mud.popup_object.show();
        }
        else if (code == ERR.died) {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
        }
        else {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
        }
    });
}

/*
 * On look at an player.
 */
MudderyScene.prototype.onPlayer = function(element) {
    var index = $(element).data("index");
    var obj_id = this.surroundings["players"][index]["id"];
    core.command.look_room_char(obj_id, function(code, data, msg) {
        if (code == 0) {
            mud.popup_object.setObject(data);
            mud.popup_object.show();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
        }
    });
}

/*
 * On go to an exit.
 */
MudderyScene.prototype.onExit = function(element) {
    var index = $(element).data("index");

    var room_map = core.map_data.getCurrentRoomMap();
    var exit_key = room_map["exits"][index]["key"];
    core.command.traverse(exit_key, function(code, data, msg) {
        if (code == 0) {
            if (data["traversed"]) {
                core.map_data.setCurrentLocation(data["location"]);
                mud.scene_window.setSurroundings(data["look_around"]);

                if ("quests" in data) {
                    mud.main_frame.handle_quests(data["quests"]);
                }
                if ("events" in data) {
                    mud.main_frame.handle_events(data["events"]);
                }
            }
            else {
                mud.popup_object.setObject(data["exit"]);
                mud.popup_object.show();
            }
        }
        else if (code == ERR.died) {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * On click the conversation button.
 */
MudderyScene.prototype.OnConversation = function() {
    mud.main_frame.pushWindow(mud.conversation_window);
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

    var room_map = core.map_data.getCurrentRoomMap();
    if (room_map && "exits" in room_map) {
        this.drawExitPaths(room_map["exits"]);
    }
}

/*
 * Clear the scene.
 */
MudderyScene.prototype.clear = function() {
    this.clearScene();
    this.clearMessages();
}

/*
 * Clear the view.
 */
MudderyScene.prototype.clearScene = function() {
    this.surroundings = null;

    this.select(".scene-name").empty();
    this.select(".scene-desc").empty();
    this.select(".scene-commands").empty();
    this.select(".scene-objects").empty();
    this.select(".scene-players").empty();
    this.select(".scene-exits td").empty();
    var svg = document.getElementById("exits-svg");
    svg.innerHTML = "";
}

/*
 * Clear the message list.
 */
MudderyScene.prototype.clearMessages = function() {
    this.select(".message-list").empty();
}

/*
 * Set character's basic information.
 */
MudderyScene.prototype.setInfo = function(name, icon) {
    this.title_bar.setInfo(name, icon);
}

/*
 * Set character's state.
 */
MudderyScene.prototype.setState = function(state) {
    this.title_bar.setState(state);
}

/*
 * Set character's state in a combat.
 */
MudderyScene.prototype.setSkillState = function(state) {
    this.title_bar.setSkillState(state);
}

/*
 *  The player is in a combat queue.
 */
MudderyScene.prototype.inCombatQueue = function() {
    this.title_bar.inCombatQueue();

    var msg = core.trans("You are in waiting queue.");
    this.displayMessage(msg);
}

/*
 * Refresh the waiting time.
 */
MudderyScene.prototype.refreshWaitingTime = function(waiting_time) {
    this.title_bar.refreshWaitingTime(waiting_time);
}

/*
 *  The player left combat queue.
 */
MudderyScene.prototype.leftCombatQueue = function() {
    this.title_bar.leftCombatQueue();
}

/*
 * Refresh the scene window.
 */
MudderyScene.prototype.refresh = function() {
    this.setSurroundings(this.surroundings);
}

/*
 * Set the scene's data.
 */
MudderyScene.prototype.setSurroundings = function(surroundings) {
    this.clearScene();
    this.surroundings = surroundings;

    // get current room's data
    var room_data = core.map_data.getCurrentRoomMap();
    if (room_data) {
        // add room's name
        var room_name = core.text2html.parseHtml(room_data["name"]);
        this.select(".scene-name").html(room_name);

        // add room's desc
        this.select(".scene-desc").html(core.text2html.parseHtml(room_data["desc"]));

        // set background
        var backview = this.select("#scene-contents");
        if ("background" in room_data && room_data["background"]) {
            var url = settings.resource_url + room_data["background"]["resource"];
            backview.css("background", "url(" + url + ") no-repeat center center");
        }
        else {
            backview.css("background", "");
        }
    }

    // set commands
    var commands = this.select(".scene-commands");
    if (!("cmds" in surroundings)) {
        surroundings["cmds"] = [];
    }
    if (surroundings["cmds"].length > 0) {
        for (var i = 0; i < surroundings["cmds"].length; i++) {
            $("<div>")
                .addClass("object-button")
                .data("index", i)
                .text(surroundings["cmds"][i]["name"])
                .appendTo(commands);
        }
        commands.show();
    }
    else {
        commands.hide();
    }

    // set room objects
    var has_objects = false;
    var objects_data = room_data["objects"];
    var objects = this.select(".scene-objects");
    if (objects_data.length > 0) {
        for (var i = 0; i < objects_data.length; i++) {
            $("<div>")
                .addClass("scene-button object-button object")
                .data("index", i)
                .text(objects_data[i]["name"])
                .appendTo(objects);
        }
        has_objects = true;
    }

    // set npcs
    var has_npcs = false;
    if (!("npcs" in surroundings)) {
        surroundings["npcs"] = [];
    }
    if (surroundings["npcs"].length > 0) {
        for (var i = 0; i < surroundings["npcs"].length; i++) {
            $("<div>")
                .addClass("scene-button object-button npc")
                .data("index", i)
                .text(surroundings["npcs"][i]["name"])
                .appendTo(objects);
        }
        has_npcs = true;
    }

    if (has_objects || has_npcs) {
        objects.show();
    }
    else {
        objects.hide();
    }

    // set players
    var players = this.select(".scene-players");
    if (!("players" in surroundings)) {
        surroundings["players"] = [];
    }
    if (surroundings["players"].length > 0) {
        // Only show 10 players.
        var count = 0;
        for (var i = 0; i < surroundings["players"].length; i++) {
            var name = surroundings["players"][i]["name"];
            if (surroundings["players"][i]["is_staff"]) {
                name += "[" + core.trans("ADMIN") + "]";
            }

            $("<div>")
                .addClass("scene-button object-button player")
                .data("index", i)
                .text(surroundings["players"][i]["name"])
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
    var exits_data = room_data["exits"];
    if (exits_data.length > 0) {
        this.setExitsMap(exits_data, room_name);
    }

    // check neighbour rooms
	core.map_data.checkNeighbourRooms();
}

/*
 * Add new objects to this scene.
 */
MudderyScene.prototype.addObject = function(obj) {
    // set object
    var index = 0;
    if (obj["type"] in this.surroundings) {
        if (obj["type"] == "npcs" ||　obj["type"] == "players") {
            for (var item in this.surroundings[obj["type"]]) {
                if (item["id"] == obj["id"]) {
                    // already has this character
                    return;
                }
            }
        }
        else {
            for (var item in this.surroundings[obj["type"]]) {
                if (item["key"] == obj["key"]) {
                    // already has this object
                    return;
                }
            }
        }

        index = this.surroundings[obj["type"]].length;
        this.surroundings[obj["type"]].push(obj)
    }
    else {
        return;
    }

    if (obj["type"] == "objects") {
        var objects = this.select(".scene-objects");
        $("<div>")
            .addClass("scene-button object-button object")
            .data("index", index)
            .text(obj["name"])
            .appendTo(objects);
        objects.show();
    }
    else if (obj["type"] == "npcs") {
        // set npcs
        var objects = this.select(".scene-objects");
        $("<div>")
            .addClass("scene-button object-button npc")
            .data("index", index)
            .text(obj["name"])
            .appendTo(objects);
        objects.show();
    }
    else if (obj["type"] == "players") {
        // set players
        if (this.surroundings["players"].length < this.max_player) {
            var players = this.select(".scene-players");
            $("<div>")
                .addClass("scene-button object-button player")
                .data("index", index)
                .text(obj["name"])
                .appendTo(players);
            players.show();
        }
    }
}

/*
 * Remove objects from this scene.
 */
MudderyScene.prototype.removeObject = function(obj) {
    // Search this object in the scene.
    var type = obj["type"];
    if (!(type in this.surroundings)) {
        return;
    }

    var index = -1;
    for (var i = 0; i < this.surroundings[type].length; i++) {
        if (this.surroundings[type][i]["id"] == obj["id"]) {
            this.surroundings[type].splice(i, 1);
            index = i;
            break;
        }
    }
    if (index < 0) {
        return;
    }

    // Remove the object button.
    var item_list = [];
    if (obj["type"] == "objects") {
        item_list = this.select(".scene-objects .object");
    }
    else if (obj["type"] == "npcs") {
        item_list = this.select(".scene-objects .npc");
    }
    else if (obj["type"] == "players") {
        item_list = this.select(".scene-players .player");
    }
    $(item_list[i]).remove();

    if (this.select(".scene-objects").children().length == 0) {
        this.select(".scene-objects").hide();
    }
    if (this.select(".scene-players").children().length == 0) {
        this.select(".scene-players").hide();
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
    this.select("#scene_obj_" + player["id"]).remove();

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
}

/*
 * Draw exit paths.
 */
MudderyScene.prototype.drawExitPaths = function(exits) {
    // draw exit lines
    var svg = document.getElementById("exits-svg");
    var namespace = "http://www.w3.org/2000/svg";

    var center_dom = this.select(".direction-4");
    if (center_dom) {
        var x1 = center_dom.position().left + center_dom.outerWidth(true) / 2;
        var y1 = center_dom.position().top + center_dom.outerHeight(true) / 2;
    }

    for (var i = 0; i < exits.length; i++) {
        try {
            var exit_dom = this.select(".exit-" + i);
            if (exit_dom) {
                var x2 = exit_dom.position().left + exit_dom.outerWidth(true) / 2;
                var y2 = exit_dom.position().top + exit_dom.outerHeight(true) / 2;
                var path = document.createElementNS(namespace, "path");
                path.setAttribute("stroke", this.path_color);
                path.setAttribute("stroke-width", this.path_width);
                path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
                svg.appendChild(path);
            }
        }
        catch (error) {
            console.error(error.message);
        }
    }
}

/*
 * Display a message in message window.
 */
MudderyScene.prototype.displayMessage = function(msg, type) {
	var message_list = this.select(".message-list");

	if (!type) {
		type = "normal";
	}

	var message_class = "common";
	if (type == "PRIVATE") {
	    message_class = "private";
	}
	else if (type == "LOCAL") {
	    message_class = "local";
	}
	else if (type == "CHANNEL") {
	    message_class = "channel";
	}

	var item = $("<div>")
		.addClass("message")
		.addClass(message_class)
		.html(msg)
		.appendTo(message_list);

	// remove old messages
	var divs = message_list.find("div");
	var size = divs.length;
	if (size > this.max_messages) {
		divs.slice(0, size - max).remove();
	}

    message_list.stop(true);
    message_list.scrollTop(message_list[0].scrollHeight);
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
 * Set character's state.
 */
MudderyTitleBar.prototype.setState = function(state) {
    if ("level" in state) {
	    this.select(".level")
	        .text(core.trans("Lv ") + state["level"]["value"])
	        .show();
	}
	else {
	    this.select(".level").hide();
	}

    /*
    if ("exp" in state && "max_exp" in state) {
        var exp_str = "";
        if (state["max_exp"]["value"] > 0) {
            exp_str = state["exp"]["value"] + "/" + state["max_exp"]["value"];
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

    if ("hp" in state && "max_hp" in state) {
        this.select(".hp-bar").width(this.full_hp_width * state["hp"]["value"] / state["max_hp"]["value"]);
		this.select(".hp-number").text(state["hp"]["value"] + "/" + state["max_hp"]["value"]);
		this.select(".hp").show();
    }
    else {
        this.select(".hp").hide();
    }
}

/*
 * Set character's state in a combat.
 */
MudderyTitleBar.prototype.setSkillState = function(state) {
    if ("level" in state) {
	    this.select(".level")
	        .text(core.trans("Lv ") + state["level"])
	        .show();
	}
	else {
	    this.select(".level").hide();
	}

    if ("hp" in state && "max_hp" in state) {
        this.select(".hp-bar").width(this.full_hp_width * state["hp"] / state["max_hp"]);
		this.select(".hp-number").text(state["hp"] + "/" + state["max_hp"]);
		this.select(".hp").show();
    }
    else {
        this.select(".hp").hide();
    }
}

/*
 * The player is in a combat queue.
 */
MudderyTitleBar.prototype.inCombatQueue = function() {
    this.select(".waiting").show();
}

/*
 * Refresh the waiting time.
 */
MudderyTitleBar.prototype.refreshWaitingTime = function(waiting_time) {
    this.select(".waiting .waiting-time").text(waiting_time);
}

/*
 * The player left a combat queue.
 */
MudderyTitleBar.prototype.leftCombatQueue = function() {
    this.select(".waiting").hide();
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

    this.equipment_pos = {};
    this.equipments = {};
	this.item_selected = null;
	this.buttons = [];
}

MudderyCharData.prototype = prototype(BaseController.prototype);
MudderyCharData.prototype.constructor = MudderyCharData;


/*
 * Bind events.
 */
MudderyCharData.prototype.bindEvents = function() {
    this.onClick(".equipments", this.onClickBody);
    this.onClick(".equipments .equipment-block", this.onClickEquipment);
    this.onClick(".item-info", ".button", this.onCommand);
}

/*
 * On the character window show.
 */
MudderyCharData.prototype.onShow = function() {
    core.command.queryEquipments(function(code, data, msg) {
        if (code == 0) {
            mud.char_data_window.setEquipments(data);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks the object link.
 */
MudderyCharData.prototype.onClickBody = function(element) {
    this.showStatus();
}

/*
 * Set player's basic data.
 */
MudderyCharData.prototype.setInfo = function(name, icon) {
    this.select(".title-bar .name").text(name);
    if (icon) {
        var url = settings.resource_url + icon;
        this.select(".title-bar .icon")
            .attr("src", url)
            .show();
    }
    else {
        this.select(".title-bar .icon").hide();
    }
}

/*
 * Set player character's information.
 */
MudderyCharData.prototype.setState = function(state) {
    this.select(".data-list>tr").remove();
    var container = this.select(".data-list");

    var row = $("<tr>");
    for (var key in state) {
        if (key.substring(0, 4) == "max_") {
            var relative_key = key.substring(4);
            if (relative_key in state) {
                // Value and max value will show in the same line, so skip max.
                continue;
            }
        }

        var value = state[key]["value"];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in state) {
            // Add max value.
            var max_value = state[max_key]["value"];

            if (max_value == null || typeof(max_value) == "undefined") {
                max_value = "--";
            }
            else if (max_value == 0 && value == 0) {
                value = "--";
                max_value = "--";
            }

            value = value + "/" + max_value;
        }

        var item = $("<td>")
            .attr("id", "info_" + key)
            .text(state[key]["name"] + ": ");

        var attr_value = $("<span>")
            .addClass("attr_value")
            .text(value)
            .appendTo(item);

        item.appendTo(row);

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
MudderyCharData.prototype.setSkillState = function(state) {
    for (var key in state) {
        if (key.substring(0, 4) == "max_") {
            var relative_key = key.substring(4);
            if (relative_key in state) {
                // Value and max value will show in the same line, so skip max.
                continue;
            }
        }

        var item = this.select("#info_" + key);

        var value = state[key];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in state) {
            // Add max value.
            var max_value = state[max_key];

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
        block.data("position", pos);
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
    this.equipments = equipments;
    var has_selected_item = false;
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

            if (this.item_selected && this.item_selected == pos) {
                has_selected_item = true;
            }
        }
        else {
            block.find(".icon").hide();
            block.find(".name").hide();
            block.find(".position-name").show();
        }
    }

    if (has_selected_item) {
        core.command.equipmentsObject(this.item_selected, function(code, data, msg) {
            if (code == 0) {
                mud.char_data_window.showEquipment(data);
            }
            else {
                mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
            }
        });
    }
    else {
        this.item_selected = null;
        this.select(".item-info").hide();
        this.select(".data-table").show();
    }
}

/*
 * On click the equipment block
 */
MudderyCharData.prototype.onClickEquipment = function(target, event) {
    event.stopPropagation();

    var position = $(target).data("position");
    if (position && position in this.equipments) {
        mud.char_data_window.item_selected = position;
        core.command.equipmentsObject(position, function(code, data, msg) {
            if (code == 0) {
                mud.char_data_window.showEquipment(data);
            }
            else {
                mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
            }
        });
    }
    else {
        this.showStatus();
    }
}

/*
 * Event when clicks a command button.
 */
MudderyCharData.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
		    this.confirmCommand(index);
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
            mud.main_frame.popupMessage(
                core.trans("Warning"),
                this.buttons[index]["confirm"],
                buttons
            );
		}
	}
}

/*
 * Confirm the command.
 */
MudderyCharData.prototype.confirmCommand = function(index) {
	var button = this.buttons[index];
	var command = button["cmd"];
    core.command.sendCommand(command, button["args"], function(code, data, msg) {
        if (code != 0) {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
        else {
            if (command == "takeoff") {
                mud.main_frame.setState(data["state"]);
                mud.char_data_window.setEquipments(data["equipments"]);
            }
        }
    });
}

/*
 * Show state view.
 */
MudderyCharData.prototype.showState = function(data) {
    this.item_selected = null;
    this.select(".item-info").hide();
    this.select(".data-table").show();
}

/*
 * Show the equipment's information.
 */
MudderyCharData.prototype.showEquipment = function(obj) {
    this.select(".item-info .icon-image").attr("src", settings.resource_url + obj["icon"]);
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
    this.select(".data-table").hide();
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
 * On the inventory window show.
 */
MudderyInventory.prototype.onShow = function() {
    this.reset();
    core.command.queryInventory(function(code, data, msg) {
        if (code == 0) {
            mud.inventory_window.setInventory(data);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks a command button.
 */
MudderyInventory.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
	        this.confirmCommand(index);
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
MudderyInventory.prototype.confirmCommand = function(index) {
	var button = this.buttons[index];
	var command = button["cmd"];
	var args = button["args"]? button["args"]: {};
	args["position"] = this.item_selected;
    core.command.sendCommand(command, args, function(code, data, msg) {
        if (code != 0) {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
        else if (code == ERR.died) {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
        }
        else {
            if (command == "equip") {
                mud.main_frame.setState(data["state"]);
                mud.inventory_window.setInventory(data["inventory"]);
            }
            else if (command == "use") {
                if (data) {
                    mud.main_frame.popupAlert(core.trans("Alert"), data["msg"]);

                    if ("state" in data) {
                        mud.main_frame.setState(data["state"]);
                    }
                    if ("inventory" in data) {
                        mud.inventory_window.setInventory(data["inventory"]);
                    }
                }
                else {
                    mud.main_frame.popupAlert(core.trans("Alert"), core.trans("No effect."));
                }
            }
            else if (command == "discard") {
                mud.inventory_window.setInventory(data["inventory"]);
            }
        }
    });
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
        core.command.inventoryObject(this.inventory[index]["position"], function(code, data, msg) {
            if (code == 0) {
                mud.inventory_window.showObject(data);
            }
            else {
                mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
            }
        });
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

        // name
        var name = core.text2html.parseHtml(obj["name"]);
        $("<div>")
            .addClass("name")
            .html(name)
            .appendTo(item);

        // number
        if (obj["number"] != 1 || !obj["can_remove"]) {
            $("<div>")
                .addClass("number")
                .text(obj["number"])
                .appendTo(item);
        }

        if (this.item_selected && this.item_selected == obj["position"]) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.command.inventoryObject(this.item_selected, "inventory");
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
    this.select(".item-info .name").html(core.text2html.parseHtml(obj["name"]));

    // number
    if (obj["number"] != 1 || !obj["can_remove"]) {
        this.select(".item-info .number")
            .html("&times;" + obj["number"])
            .show();
    }
    else {
        this.select(".item-info .number").hide();
    }

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

    this.item_selected = obj["position"];

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
 * Called when the controller shows.
 */
MudderySkills.prototype.onShow = function() {
    this.reset();
    this.select(".skill-info").hide();
    core.command.queryAllSkills(function(code, data, msg) {
        if (code == 0) {
            mud.skills_window.setSkills(data);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onSelect = function(element) {
    var index = $(element).data("index");
    if (index < this.skills.length) {
        this.item_selected = this.skills[index].key;
        core.command.querySkill(this.item_selected, function(code, data, msg) {
            if (code == 0) {
                mud.skills_window.showSkill(data);
            }
            else {
                mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
            }
        });
    }
}

/*
 * Event when clicks a command button.
 */
MudderySkills.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	var button = this.buttons[index];
	if ("cmd" in button && "args" in button) {
	    if (!button["confirm"]) {
		    this.confirmCommand(index);
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
        mud.main_frame.popupMessage(
            core.trans("Warning"),
            button["confirm"],
            buttons);
		}
	}
}

/*
 * Confirm the command.
 */
MudderySkills.prototype.confirmCommand = function(index) {
	var button = this.buttons[index];
	var command = button["cmd"];
    core.command.sendCommand(command, button["args"], function(code, data, msg) {
        if (code != 0) {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
        else if (code == ERR.died) {
            mud.main_frame.popupAlert(core.trans("Alert"), core.trans("You are died."));
        }
        else {
            if (command == "cast_skill") {
                // set skill cd
                var skill_cd = data["skill_cd"];
            	mud.combat_window.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);

                var result = data["result"];

                if ("state" in result && core.data_handler.character_id in result["state"]) {
                    mud.main_frame.setSkillStatus(result["state"][core.data_handler.character_id]);
                }

                var message = "";
                if ("cast" in result && result["cast"]) {
                    message += result["cast"];
                }
                if ("result" in result && result["result"]) {
                    if (message) {
                        message += "{/";
                    }
                    message += result["result"];
                }
                if (message) {
                    mud.main_frame.popupMessage(core.trans("Skill"), message);
                }
                else {
                    mud.main_frame.popupMessage(core.trans("Skill"), core.trans("No result."));
                }
            }
        }
    });
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

        if (obj["key"] == this.item_selected) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.command.querySkill(this.item_selected, function(code, data, msg) {
            if (code == 0) {
                mud.skills_window.showSkill(data);
            }
            else {
                mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
            }
        });
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
 * Called when the controller shows.
 */
MudderyQuests.prototype.onShow = function() {
    this.reset();
    this.select(".quest-info").hide();
    core.command.queryAllQuests(function(code, data, msg) {
        if (code == 0) {
            mud.quests_window.setQuests(data);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks the quest link.
 */
MudderyQuests.prototype.onSelect = function(element) {
    var index = $(element).data("index");
    if (index < this.quests.length) {
        var key = this.quests[index].key;
        this.item_selected = key;
        this.showQuest(this.quests[index]);
    }
}

/*
 * Event when clicks a command button.
 */
MudderyQuests.prototype.onCommand = function(element) {
	var index = $(element).data("index");
	if ("cmd" in this.buttons[index] && "args" in this.buttons[index]) {
	    if (!this.buttons[index]["confirm"]) {
		    this.confirmCommand(index);
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
MudderyQuests.prototype.confirmCommand = function(index) {
	var button = this.buttons[index];
	var command = button["cmd"];
    core.command.sendCommand(command, button["args"], function(code, data, msg) {
        if (code != 0) {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
        else {
            if (command == "give_up_quest") {
                var msg = core.trans("Gave up quest {C%s{n.").replace("%s", data["name"]);
                mud.scene_window.displayMessage(core.text2html.parseHtml(msg));

                mud.quests_window.setQuests(data["all_quests"]);
            }
        }
    });
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

        if (obj["key"] == this.item_selected) {
            has_selected_item = true;
        }
    }

    if (has_selected_item) {
        core.command.queryQuest(this.item_selected);
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
 * Honour Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyHonour = function(el) {
	BaseController.call(this, el);

	this.min_honour_level = 1;
}

MudderyHonour.prototype = prototype(BaseController.prototype);
MudderyHonour.prototype.constructor = MudderyHonour;

/*
 * Called when the controller shows.
 */
MudderyHonour.prototype.onShow = function() {
    var container = this.select(".rank-table");
    container.empty();
    core.command.getRankings(function(code, data, msg) {
        if (code == 0) {
            mud.honour_window.setRankings(data);
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Bind events.
 */
MudderyHonour.prototype.bindEvents = function() {
    this.onClick(".button-queue", this.onQueueUpCombat);
    this.onClick(".button-quit", this.onQuitCombatQueue);
}

/*
 * Event when clicks the queue up button.
 */
MudderyHonour.prototype.onQueueUpCombat = function(element) {
    if (core.data_handler.character_level < this.min_honour_level) {
        mud.main_frame.popupAlert(core.trans("Warning"),
                                  core.trans("You need to reach level ") +
	                              this.min_honour_level + core.trans("."));
        return;
    }

    core.command.queueUpCombat(function(code, data, msg) {
        if (code == 0) {
            mud.main_frame.inCombatQueue();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Event when clicks the quit queue button.
 */
MudderyHonour.prototype.onQuitCombatQueue = function(element) {
    core.command.quitCombatQueue(function(code, data, msg) {
        if (code == 0) {
            mud.main_frame.leftCombatQueue();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Set the minimum level that a player can attend a honour combat.
 */
MudderyHonour.prototype.setMinHonourLevel = function(level) {
	this.min_honour_level = level;
}

/*
 * Set top characters.
 */
MudderyHonour.prototype.setRankings = function(rankings) {
    var container = this.select(".rank-list");
    container.empty();

    for (var i in rankings) {
        var data = rankings[i];

        var item = $("<div>")
            .addClass("rank-item")
            .data("index", i)
            .appendTo(container);

        // Ranking
        $("<span>")
            .addClass("ranking")
            .text("No. " + data["ranking"])
            .appendTo(item);

        // Name
        $("<span>")
            .addClass("name")
            .html(core.text2html.parseHtml(data["name"]))
            .appendTo(item);

        // Honour
        $("<span>")
            .addClass("honour")
            .text(data["honour"])
            .appendTo(item);
    }
}

/*
 * The player is in a combat queue.
 */
MudderyHonour.prototype.inCombatQueue = function() {
    this.select(".action-block-queue").hide();
    this.select(".action-block-waiting").show();
}

/*
 * Refresh the waiting time.
 */
MudderyHonour.prototype.refreshWaitingTime = function(waiting_time) {
    this.select(".queue-waiting-time").text(waiting_time);
}

/*
 * The player left a combat queue.
 */
MudderyHonour.prototype.leftCombatQueue = function() {
    this.select(".action-block-waiting").hide();
    this.select(".action-block-queue").show();
    this.select(".queue-waiting-time").text("");
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
 * Called when the controller shows.
 */
MudderyMap.prototype.onShow = function() {
    this.showMap(core.map_data.getCurrentLocation());
}

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

    if (!location) {
        return;
    }

    var current_area_key = location["area"];
    var current_room_key = location["room"];

	if (!(current_room_key in core.map_data._map_rooms)){
		// does not have current location, can not show map.
		return;
	}
	var current_room = core.map_data._map_rooms[current_room_key];

	var map_width = this.select("#map-svg").width();
	var map_height = this.select("#map-svg").height();

	// var scale = this.scale;
	var room_size = this.room_size;
	var origin_x = map_width / 2;
	var origin_y = map_height / 2;

	var svg = document.getElementById("map-svg");
	var namespace = "http://www.w3.org/2000/svg";

	if (current_room["pos"]) {
		// set origin point
		//origin_x -= current_room["pos"][0] * scale;
		//origin_y -= -current_room["pos"][1] * scale;
		origin_x -= current_room["pos"][0];
		origin_y -= current_room["pos"][1];
	}

    // title and background
	if (current_area_key in core.map_data._map_areas){
		var area_name = core.text2html.parseHtml(core.map_data._map_areas[current_area_key]["name"]);
		if (area_name) {
			this.select(".header-text").html(area_name);
		}

	    var area_background = core.map_data._map_areas[current_area_key]["background"];
	    if (area_background) {
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

            var map_back = settings.resource_url + area_background["resource"];
            var background = document.createElementNS(namespace, "image");
            background.setAttribute("x", x);
            background.setAttribute("y", y);
            background.setAttribute("width", area_background["width"]);
            background.setAttribute("height", area_background["height"]);
            background.href.baseVal = settings.resource_url + area_background["resource"];
            svg.appendChild(background);
        }
	}

    // draw path
	if (current_room["pos"] && core.map_data._map_paths) {
		// get path positions
		var path_data = [];
		for (var from_room_key in core.map_data._map_paths) {
			if (!(from_room_key in core.map_data._map_rooms)) {
			    continue;
			}

            var from_room = core.map_data._map_rooms[from_room_key];
            var from_area_key = from_room["area"];
            if (from_area_key != current_area_key) {
                continue;
            }

            var from = from_room["pos"];
            if (!from) {
                continue;
            }

            for (var to_room_key in core.map_data._map_paths[from_room_key]) {
                if (!(core.map_data._map_paths[from_room_key][to_room_key] in core.map_data._map_rooms)) {
                    continue;
                }

                var to_room = core.map_data._map_rooms[core.map_data._map_paths[from_room_key][to_room_key]];
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

    // draw room
	if (core.map_data._map_rooms) {
		// get room positions
		var room_data = [];
		var current_room_index = -1;

		if (current_room["pos"]) {
			var count = 0;
			for (var room_key in core.map_data._map_rooms) {
				var room = core.map_data._map_rooms[room_key];
				if (room["pos"]) {
					var area_key = room["area"];
					if (area_key != current_area_key) {
						continue;
					}

					room_data.push({"name": core.utils.truncate_string(room["name"], 10, true),
									"icon": room["icon"]? settings.resource_url + room["icon"]: null,
									"area": room["area"],
									"pos": room["pos"]});
					if (room_key == current_room_key) {
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

    this.combat_result = new MudderyCombatResult(this.select(".combat-result"));

	this.self_id = "";
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
 * Document ready event.
 */
MudderyCombat.prototype.init = function() {
    this.combat_result.init();
    this.combat_result.hide();
    this.bindEvents();
}

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

	core.command.castCombatSkill(key, this.target, function(code, data, msg) {
	    if (code == 0) {
	        // reset skill's cd
	        if ("skill_cd" in data) {
	            mud.combat_window.setSkillCD(data["skill_cd"]["key"], data["skill_cd"]["cd"], data["skill_cd"]["gcd"]);
	        }
	    }
	    else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
	});
}

/*
 * Reset the combat box.
 */
MudderyCombat.prototype.reset = function() {
	this.select(".desc").empty();
	this.select(".game-time").empty();

	// Remove characters that are not template.
	this.select(".characters").empty();

	// Remove combat messages.
	this.select(".message-list").empty();

	// Remove skill buttons that are not template.
	this.select(".buttons").empty();

	this.self_id = "";
	this.target = "";
	this.combat_finished = true;
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
MudderyCombat.prototype.setCombat = function(desc, timeout, characters, self_id) {
	if (!this.combat_finished) {
		return;
	}
	this.combat_finished = false;

	this.self_id = self_id;

	var self_team = "";
	for (var i in characters) {
		if (characters[i]["id"] == self_id) {
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

		this.select(".combat-time").text(timeout);
		this.select(".timeout").show();
		this.interval_id = window.setInterval(function() {
		    mud.combat_window.refreshTimeout();
		}, 1000);
	}
	else {
		this.select(".combat-time").empty();
		this.select(".timeout").hide();
	}

	// add characters
	var teammate_number = 0;
	var enemy_number = 0;
	var top = 10;
	var line_height = 30;

	for (var i in characters) {
		var character = characters[i];
		var obj_id = character["id"];

		var item = $("<div>")
            .attr("id", "combat-char-" + obj_id)
        	.data("obj_id", character["id"]);

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

		if (this.self_id == obj_id) {
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
				this.target = character["id"];
			}
		}

		item.appendTo(this.select(".characters"));
	}

    this.character_hp_width = $(".character-hp").width();
}

/*
 * Set combat commands.
 */
MudderyCombat.prototype.setCommands = function(commands) {
	var container = this.select(".skill-list");
	container.empty();

    for (var i in commands) {
        var command = commands[i];
        this.skill_cd_time[command["key"]] = command["cd"];

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
		this.displayMessage(message);
	}

	if ("skill" in data) {
		if (data["skill"] == "skill_normal_hit" ||
			data["skill"] == "skill_dunt") {

			var caller = $('#combat-char-' + data["caller"]);
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
				var item_id = "#combat-char-" + data["target"] + ".state";
				$(item_id).text(core.trans("Escaped"));
			}
		}
	}

	// Update state.
	if ("states" in data) {
		this.updateStates(data["states"]);
	}
}

/*
 * Display a message in message window.
 */
MudderyCombat.prototype.displayMessage = function(msg) {
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
 * Update character's state.
 */
MudderyCombat.prototype.updateStates = function(states) {
	for (var key in states) {
		var hp_bar = "#combat-char-" + key + " .character-hp-bar";
		$(hp_bar).width(this.character_hp_width * states[key]["hp"] / states[key]["max_hp"]);

		if (this.self_id == key) {
		    this.select(".hp-bar").width(this.full_hp_width * states[key]["hp"] / states[key]["max_hp"]);
		    this.select(".hp-number").text(states[key]["hp"] + "/" + states[key]["max_hp"]);
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
MudderyCombat.prototype.leaveCombat = function() {
	this.combat_finished = true;
	if (this.interval_id != null) {
		window.clearInterval(this.interval_id);
		this.interval_id = null;
	}

    mud.main_frame.popWindow(this);
    mud.scene_window.refresh();
    if (mud.popup_dialogue.hasDialogue()) {
        mud.popup_dialogue.show();
    }
}

/*
 * The combat has finished.
 */
MudderyCombat.prototype.combatFinish = function(data) {
	this.combat_finished = true;
	if (this.interval_id != null) {
		window.clearInterval(this.interval_id);
		this.interval_id = null;
	}

    this.combat_result.reset();
	this.combat_result.setResult(data["type"], data["result"], data["rewards"]);
	this.combat_result.show();

	if ("state" in data) {
	    mud.main_frame.setState(data["state"]);
	}
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

    $("#combat-window .combat-time").text(remain);
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
    this.select(".result-honour-block").hide();
    this.select(".result-honour").empty();
    this.select(".result-exp-block").hide();
    this.select(".result-exp").empty();
	this.select(".result-level-up-block").hide();
    this.select(".result-level-up");
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
	core.command.leaveCombat(function(code, data, msg) {
	    if (code == 0) {
	        mud.main_frame.setState(data["state"]);
            core.map_data.setCurrentLocation(data["location"]);
            mud.scene_window.setSurroundings(data["look_around"]);

            if ("quests" in data) {
                mud.main_frame.handle_quests(data["quests"]);
            }
            if ("events" in data) {
                mud.main_frame.handle_events(data["events"]);
            }
            if ("die" in data) {
                var msg = core.text2html.parseHtml("{R" + core.trans("You died.") + "{n");
                mud.scene_window.displayMessage(msg);
            }
            if ("reborn_time" in data) {
                var msg = core.trans("You will be reborn in {C%s{n seconds.").replace("%s", data["reborn_time"]);
                mud.scene_window.displayMessage(core.text2html.parseHtml(msg));
            }

            mud.combat_window.leaveCombat();
        }
        else {
            mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
        }
    });
}

/*
 * Set result data.
 */
MudderyCombatResult.prototype.setResult = function(type, result, rewards) {
	if (!result) {
		return;
	}

	var header = "";
	if (result == "COMBAT_ESCAPED") {
	   header = core.trans("Escaped !");
	}
	else if (result == "COMBAT_WIN") {
		header = core.trans("You win !");
	}
	else if (result == "COMBAT_LOSE") {
		header = core.trans("You lost !");
	}
	else if (result == "COMBAT_DRAW") {
		header = core.trans("Draw !");
	}

	this.select(".header-text").text(header);

    if (rewards) {
        if ("honour" in rewards) {
            this.setGetHonour(rewards["honour"]);
        }

        if ("exp" in rewards) {
            this.setGetExp(rewards["exp"]);
        }

        if ("level_up" in rewards) {
            this.setLevelUp(rewards["level_up"]);
        }

        if ("get_objects" in rewards) {
            this.setGetObjects(rewards["get_objects"]["objects"]);
            if ("quests" in rewards["get_objects"]) {
                mud.main_frame.handle_quests(rewards["get_objects"]["quests"]);
            }
        }
    }
}

/*
 * Show the honours that the player get.
 */
MudderyCombatResult.prototype.setGetHonour = function(honour) {
	this.select(".result-honour").text(honour);
	this.select(".result-honour-block").show();
}

/*
 * Show the experiences that the player get.
 */
MudderyCombatResult.prototype.setGetExp = function(exp) {
	this.select(".result-exp").text(exp);
	this.select(".result-exp-block").show();
}

/*
 * Show the level that the player get.
 */
MudderyCombatResult.prototype.setLevelUp = function(level) {
	this.select(".result-level-up").text(level);
	this.select(".result-level-up-block").show();
}

/*
 * Show the objects that the player get.
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
    mud.game_window.showWindow(mud.scene_window);
}

/*
 * Event when clicks goods.
 */
MudderyShop.prototype.onClickGoods = function(element) {
    var index = $(element).data("index");
    if (index < this.goods.length) {
        var goods = this.goods[index];
        this.goods_detail.reset();
        this.goods_detail.setGoods(this.npc, this.key, goods);
        this.goods_detail.show();
    }
}

/*
 * Reset the shop
 */
MudderyShop.prototype.reset = function() {
	this.select(".header-text").html(core.trans("Shop"));
    this.select(".shop-icon-img").hide();
    this.select(".desc-content").html("");
    this.select(".goods-list").empty();
}

/*
 * Set shop's goods.
 */
MudderyShop.prototype.setShop = function(data) {
    this.npc = data["npc"];
    this.key = data["key"];
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

	container.scrollTop(0);
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
        core.command.buy(this.npc, this.shop, this.goods["index"], function(code, data, msg) {
            if (code == 0) {
                mud.main_frame.popupAlert(core.trans("Alert"), core.trans("Purchase successful!"));
            }
            else if (code == ERR.can_not_buy) {
                mud.main_frame.popupAlert(core.trans("Alert"), core.trans(msg));
            }
            else {
                mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
            }
        });
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
MudderyGoodsDetail.prototype.setGoods = function(npc, shop, goods) {
    this.npc = npc;
    this.shop = shop;
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
    this.select(".header-text").html(goods_name);

    // set price
    this.select(".goods-price").text(goods["price"] + goods["unit"]);

    // set desc
    this.select(".goods-desc").html(core.text2html.parseHtml(goods["desc"]));
}


/******************************************
 *
 * Conversation Window
 *
 ******************************************/

/*
 * Derive from the base class.
 */
MudderyConversation = function(el) {
	BaseController.call(this, el);

	// Default send to local location.
	this.conversation_type = "LOCAL";
	this.target = "";
	this.max_messages = 200;
}

MudderyConversation.prototype = prototype(BaseController.prototype);
MudderyConversation.prototype.constructor = MudderyConversation;

/*
 * Bind events.
 */
MudderyConversation.prototype.bindEvents = function() {
    this.onClick(".button-close", this.onClose);
    this.onClick(".channel-list", ".button-channel", this.onSelectChannel);
    this.onClick(".button-send", this.onSend);
}

/*
 * On click the close button.
 */
MudderyConversation.prototype.onClose = function() {
    mud.main_frame.popWindow(this);
}

/*
 * On click the channel button.
 */
MudderyConversation.prototype.onSelectChannel = function(element) {
	this.conversation_type = $(element).data("type");
	this.target = $(element).data("target");

	this.select(".channel-list .button-channel").removeClass("active");
	$(element).addClass("active");
}

/*
 * On click the send button.
 */
MudderyConversation.prototype.onSend = function() {
	var message = this.select(".input-box").val();
	this.select(".input-box").val("");

	if (!message) {
		return;
	}

    var target = this.target;
    if (this.conversation_type == "LOCAL") {
        var location = core.map_data.getCurrentLocation();
        target = location["room"];
    }
    else if (this.conversation_type == "CHANNEL") {
        target = this.target;
    }

	core.command.say(this.conversation_type, target, message, function(code, data, msg) {
	    if (code != 0) {
	        mud.main_frame.popupAlert(core.trans("Error"), core.trans(msg));
	    }
	});
}

/*
 * Clear all channels' messages.
 */
MudderyConversation.prototype.clearChannels = function() {
	var container = this.select(".channel-list");
	container.empty();
}

/*
 * Set available channels.
 */
MudderyConversation.prototype.setChannels = function(channels) {
	var container = this.select(".channel-list");
	container.empty();

	for (var key in channels) {
		var channel = channels[key];

		$("<div>")
		    .addClass("button-channel")
		    .data("type", channel["type"])
		    .data("target", key)
		    .text(channel["name"])
		    .appendTo(container);
	}

	// Add local room.
    $("<div>")
        .addClass("button-channel active")
        .data("type", "LOCAL")
        .text(core.trans("LOCAL"))
        .appendTo(container);
}

/*
 * Get a message.
 */
MudderyConversation.prototype.getMessage = function(message) {
	var message_class = "common";
	if (message["type"] == "PRIVATE") {
	    message_class = "private";
	}
	else if (message["type"] == "LOCAL") {
	    message_class = "local";
	}
	else if (message["type"] == "CHANNEL") {
	    message_class = "channel";
	}

	var prefix = "";
    if (message["type"] == "PRIVATE") {
	    if (message["from_id"] == core.data_handler.character_id) {
	        prefix = core.trans("TO[") + message["channel"] + "]";
	    }
	    else {
	        prefix = core.trans("FROM[") + message["from_name"] + "]";
	    }
	}
	else if (message["type"] == "LOCAL" || message["type"] == "CHANNEL") {
	    prefix = "[" + message["channel"] + "][" + message["from_name"] + "]";
	}

    var out_text = prefix + " " + message["msg"];
    var message_list = this.select(".message-list");
    var item = $("<div>")
        .addClass("message")
        .addClass(message_class)
        .text(out_text)
        .appendTo(message_list);

	var divs = message_list.find("div");
	var size = divs.length;
	if (size > this.max_messages) {
		divs.slice(0, size - max).remove();
	}

    var message_box = this.select(".messages");
    message_box.scrollTop(message_list[0].scrollHeight);

    mud.scene_window.displayMessage(out_text, message["type"]);
}
