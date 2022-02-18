
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
     	var parsed = JSON.parse(message);
     	var all_data = parsed.data;

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

                    if (key == "msg") {
                        var msg = core.text2html.parseHtml(data[key]);
                        mud.scene_window.displayMessage(msg);
                    } else if (key == "alert") {
                        mud.main_frame.popupMessage(core.trans("Alert"), data[key]);
                    } else if (key == "out") {
                        mud.scene_window.displayMessage(data[key], "out");
                    } else if (key == "err") {
                        mud.scene_window.displayMessage(data[key]);
                    } else if (key == "sys") {
                        mud.scene_window.displayMessage(data[key], "sys");
                    } else if (key == "debug") {
                        mud.scene_window.displayMessage(data[key], "debug");
                    } else if (key == "prompt") {
                        mud.scene_window.displayMessage(data[key], "prompt");
                    } else if (key == "game_name") {
                        mud.login_window.setGameName(data[key]);
                    } else if (key == "conn_screen") {
                        mud.login_window.setConnScreen(data[key]);
                    } else if (key == "min_honour_level") {
                        mud.honour_window.setMinHonourLevel(data[key]);
                    } else if (key == "look_around") {
                        mud.scene_window.setSurroundings(data[key]);
                    } else if (key == "obj_moved_in") {
                        mud.main_frame.objMovedIn(data[key]);
                    } else if (key == "obj_moved_out") {
                        mud.main_frame.objMovedOut(data[key]);
                    } else if (key == "player_online") {
                        mud.main_frame.playerOnline(data[key]);
                    } else if (key == "player_offline") {
                        mud.main_frame.playerOffline(data[key]);
                    } else if (key == "look_obj") {
                        mud.popup_object.setObject(data[key]);
                        mud.popup_object.show();
                    } else if (key == "skill_info") {
                        mud.skills_window.showSkill(data[key]);
                    } else if (key == "quest_info") {
                        mud.quests_window.showQuest(data[key]);
                    } else if (key == "inventory_obj") {
                        mud.inventory_window.showObject(data[key]);
                    } else if (key == "equipments_obj") {
                        mud.char_data_window.showEquipment(data[key]);
                    } else if (key == "dialogue") {
                        mud.popup_dialogue.setDialogue(data[key]);
                        if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                            mud.popup_dialogue.show();
                        }
                    } else if (key == "status") {
                        var status = data[key];
                        mud.main_frame.setStatus(status);
                    } else if (key == "equipment_pos") {
                        mud.char_data_window.setEquipmentPos(data[key]);
                    } else if (key == "equipments") {
                        mud.char_data_window.setEquipments(data[key]);
                    } else if (key == "inventory") {
                        mud.inventory_window.setInventory(data[key]);
                    } else if (key == "skills") {
                        core.data_handler.setSkills(data[key]);
                        mud.skills_window.setSkills(data[key]);
                    } else if (key == "quests") {
                        mud.quests_window.setQuests(data[key]);
                    } else if (key == "get_objects") {
                        mud.main_frame.showGetObjects(data[key]);
                    } else if (key == "joined_combat") {
                        mud.main_frame.showCombat(data[key]);
                    } else if (key == "combat_finish") {
                        mud.combat_window.combatFinish(data[key]);
                    } else if (key == "combat_info") {
                        var info = data[key];
                        mud.combat_window.setCombat(info["desc"],
                            info["timeout"],
                            info["characters"],
                            core.data_handler.character_id);
                    } else if (key == "combat_status") {
                        mud.combat_window.updateStatus(data[key]);
                    } else if (key == "combat_commands") {
                        mud.combat_window.setCommands(data[key]);
                    } else if (key == "skill_cd") {
                        var skill_cd = data[key];
                        mud.main_frame.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                    } else if (key == "skill_cast") {
                        mud.main_frame.setSkillCast(data[key]);
                    } else if (key == "get_exp") {
                        var get_exp = data[key];
                        mud.main_frame.showGetExp(get_exp["exp"]);
                    } else if (key == "login") {
                        mud.main_frame.onLogin(data[key]);
                    } else if (key == "logout") {
                        mud.main_frame.onLogout(data[key]);
                    } else if (key == "pw_changed") {
                        mud.main_frame.popWindow(mud.password_window);
                    } else if (key == "unpuppet") {
                        mud.main_frame.onUnpuppet(data[key]);
                    } else if (key == "char_all") {
                        mud.select_char_window.setCharacters(data[key]);
                    } else if (key == "max_char") {
                        mud.select_char_window.setMaxNumber(data[key]);
                    } else if (key == "char_created") {
                        mud.new_char_window.onCharacterCreated(data[key]);
                    } else if (key == "char_deleted") {
                    } else if (key == "puppet") {
                        mud.main_frame.onPuppet(data[key]);
                    } else if (key == "channels") {
                        mud.conversation_window.setChannels(data[key]);
                    } else if (key == "conversation") {
                        mud.conversation_window.getMessage(data[key]);
                    } else if (key == "current_location") {
                        core.map_data.setCurrentLocation(data[key]);
                    } else if (key == "reveal_maps") {
                        core.map_data.revealMaps(data[key]);
                    } else if (key == "shop") {
                        mud.game_window.showShop(data[key]);
                    } else if (key == "rankings") {
                        mud.honour_window.setRankings(data[key]);
                    } else if (key == "in_combat_queue") {
                        mud.main_frame.inCombatQueue(data[key]);
                    } else if (key == "left_combat_queue") {
                        mud.main_frame.leftCombatQueue(data[key]);
                    } else if (key == "prepare_match") {
                        mud.main_frame.prepareMatch(data[key]);
                    } else if (key == "match_rejected") {
                        mud.main_frame.matchRejected(data[key]);
                    } else {
                        mud.scene_window.displayMessage(data[key]);
                    }
                } catch (error) {
                    console.log(key, data[key])
                    console.error(error.stack);
                }
            }
        }
    },
}
