
/***************************************
 *
 * Deal with all received messages
 * and send them to other units.
 *
 ***************************************/

MudderyClient = function() {
}

MudderyClient.prototype = {
    // Event when client finishes loading
    init: function() {
        // This is safe to call, it will always only
        // initialize once.
        Connection.init();

        // register listeners
        Connection.bindEvents({
            on_open: this.onConnectionOpen,
            on_close: this.onConnectionClose,
            on_message: this.onReceiveMessage,
        });

        Connection.connect();

        if (Connection.state() == WebSocket.CLOSED) {
            this.showAlert(core.trans("Error"), core.trans("Can not connect to the server."));
            return;
        }

        // set an idle timer to send idle every 30 seconds,
        // to avoid proxy servers timing out on us
        setInterval(function() {
            // Connect to server
            if (Connection.isConnected()) {
                Connection.send("idle");
            }
        }, 30000);
    },

 	onReceiveMessage: function(message) {
 		core.client.handle_message(message);
 	},

 	onConnectionClose: function() {
 	    mud.main_frame.onConnectionClose();
 	},

 	onConnectionOpen: function() {
        mud.main_frame.onConnectionOpen();
    },

    showAlert: function(msg) {
        mud.main_frame.popupAlert(msg);
    },

    // handle commands from the server
    handle_message: function(message) {
     	var all_data = JSON.parse(message);

     	// all_data can be a dict or an array of dicts.
     	if (!(all_data instanceof Array)) {
     	    all_data = [all_data];
        }

     	for (var i = 0; i < all_data.length; i++) {
     	    var data = all_data[i];
            for (var key in data) {
                try {
                    var log_data = {}
                    log_data[key] = data[key];

                    if (key == "response") {
                        core.command.respond(data[key].sn, data[key].code, data[key].data, data[key].msg);
                    }
                    else if (key == "msg") {
                        var msg = core.text2html.parseHtml(data[key]);
                        mud.scene_window.displayMessage(msg);
                    } else if (key == "alert") {
                        mud.main_frame.popupMessage(core.trans("Alert"), data[key]);
                    } else if (key == "obj_moved_in") {
                        mud.main_frame.objMovedIn(data[key]);
                    } else if (key == "obj_moved_out") {
                        mud.main_frame.objMovedOut(data[key]);
                    } else if (key == "state") {
                        var state = data[key];
                        mud.main_frame.setState(state);
                    } else if (key == "attack") {
                        mud.main_frame.handle_combat(data[key], false);
                    } else if (key == "combat_finish") {
                        mud.combat_window.combatFinish(data[key]);
                    } else if (key == "combat_status") {
                        mud.combat_window.updateStatus(data[key]);
                    } else if (key == "conversation") {
                        mud.conversation_window.getMessage(data[key]);
                    } else if (key == "current_location") {
                        core.map_data.setCurrentLocation(data[key]);
                    } else if (key == "rankings") {
                        mud.honour_window.setRankings(data[key]);
                    } else if (key == "in_combat_queue") {
                        mud.main_frame.inCombatQueue(data[key]);
                    } else if (key == "left_combat_queue") {
                        mud.main_frame.leftCombatQueue(data[key]);
                    } else if (key == "combat_skill_cast") {
                        mud.combat_window.setSkillCast(data[key]);
                    } else if (key == "prepare_match") {
                        mud.main_frame.prepareMatch(data[key]);
                    } else if (key == "match_rejected") {
                        mud.main_frame.matchRejected(data[key]);
                    } else {
                        mud.main_frame.popupAlert(core.trans("Error"), "Unknown message: " + key);
                    }
                } catch (error) {
                    console.log(key, data[key])
                    console.error(error.stack);
                }
            }
        }
    },
}
