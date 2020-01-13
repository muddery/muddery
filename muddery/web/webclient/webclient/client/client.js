
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
        Evennia.init();

        // register listeners
        Evennia.emitter.on("text", this.onText);
        //Evennia.emitter.on("prompt", onPrompt);
        //Evennia.emitter.on("default", onDefault);
        Evennia.emitter.on("connection_close", this.onConnectionClose);
        // silence currently unused events
        Evennia.emitter.on("connection_open", this.onConnectionOpen);
        //Evennia.emitter.on("connection_error", onSilence);

        // set an idle timer to send idle every 3 minutes,
        // to avoid proxy servers timing out on us
        setInterval(function() {
            // Connect to server
            if (Evennia.isConnected()) {
                Evennia.msg("text", ["idle"], {});
            }
        },
        60000*3
        );

        if (Evennia.state() == WebSocket.CLOSED) {
            this.showAlert("Can not connect to the server.");
            return;
        }
    },

 	onText: function(args, kwargs) {
 	    for (var i = 0; i < args.length; i++) {
 		    core.client.doShow("out", args[i]);
 		}
 	},

 	onConnectionClose: function() {
 	    mud.main_frame.onConnectionClose();
 	},

 	onConnectionOpen: function() {
        mud.main_frame.onConnectionOpen();
    },

    showAlert: function(msg) {
        mud.main_frame.showAlert(msg);
    },

    doShow: function(type, msg) {
        var data = null;
        var context = null;
        
        if (type == "out") {
            try {
                var decode = JSON.parse(msg);
                
                if (typeof(decode) == "object") {
                    // Json object.
                    data = decode["data"];
                    context = decode["context"];

                    if (typeof(data) == "string") {
                        data = {"msg": data};
                    }
                }
                else if (typeof(decode) == "string") {
                    // String
                    data = {"msg": decode};
                }
                else {
                    // Other types, treat them as normal text messages.
                    data = {"msg": msg};
                }
            }
            catch(err) {
                // Not JSON packed, treat it as a normal text message.
                data = {"msg": msg};
            }
        }
        else if (type == "err") {
            data = {"err": msg};
        }
        else if (type == "sys") {
            data = {"sys": msg};
        }
        else if (type == "prompt") {
            data = {"prompt": msg};
        }
        else if (type == "debug") {
            data = {"debug": msg};
        }
        else {
            data = {"msg": msg};
        }
                    
        this.displayData(data, context);
    },

    // display all kinds of data
    displayData : function(data, context) {
        for (var key in data) {
            try {
                log(key, data[key]);

                if (key == "settings") {
                    mud.main_frame.setClient(data[key]);
                }
                else if (key == "msg") {
                	var msg = core.text2html.parseHtml(data[key]);
                    mud.message_window.displayMessage(msg);
                }
                else if (key == "alert") {
              		mud.main_frame.showAlert(data[key]);
                }
                else if (key == "out") {
                    mud.message_window.displayMessage(data[key], "out");
                }
                else if (key == "err") {
                    mud.message_window.displayMessage(data[key]);
                }
                else if (key == "sys") {
                    mud.message_window.displayMessage(data[key], "sys");
                }
                else if (key == "debug") {
                	mud.message_window.displayMessage(data[key], "debug");
                }
                else if (key == "prompt") {
                	mud.message_window.displayMessage(data[key], "prompt");
                }
                else if (key == "game_name") {
                    mud.login_window.setGameName(data[key]);
                }
                else if (key == "conn_screen") {
                    mud.login_window.setConnScreen(data[key]);
                }
                else if (key == "look_around") {
                    mud.scene_window.setScene(data[key]);
                }
                else if (key == "obj_moved_in") {
                    mud.main_frame.showObjMovedIn(data[key]);
                }
                else if (key == "obj_moved_out") {
                    mud.main_frame.showObjMovedOut(data[key]);
                }
                else if (key == "player_online") {
                    mud.main_frame.showPlayerOnline(data[key]);
                }
                else if (key == "player_offline") {
                    mud.main_frame.showPlayerOffline(data[key]);
                }
                else if (key == "look_obj") {
                    if (context == "inventory") {
                        mud.inventory_window.showObject(data[key]);
                    }
                    else if (context == "scene") {
        			    mud.popup_object.setObject(data[key]);
        			    mud.popup_object.show();
        			}
                }
                else if (key == "dialogue") {
                    mud.popup_dialogue.setDialogue(data[key], core.data_handler.getEscapes());
                    if (mud.popup_dialogue.hasDialogue() && !mud.main_frame.isWindowShow(mud.combat_window)) {
                        mud.popup_dialogue.show();
                    }
                }
                else if (key == "status") {
                    var status = data[key];
                    mud.main_frame.setStatus(status);
                }
                else if (key == "equipment_pos") {
                    mud.char_data_window.setEquipmentPos(data[key]);
                }
                else if (key == "equipments") {
			        mud.char_data_window.setEquipments(data[key]);
                }
                else if (key == "inventory") {
                    mud.inventory_window.setInventory(data[key]);
                }
                else if (key == "skills") {
                    core.data_handler.setSkills(data[key]);
                    mud.skills_window.setSkills(data[key]);
                }
                else if (key == "quests") {
                	mud.quests_window.setQuests(data[key]);
                }
                else if (key == "get_objects") {
                	var get_objects = data[key];
                    mud.main_frame.showGetObjects(get_objects["accepted"], get_objects["rejected"]);
                }
                else if (key == "joined_combat") {
                    mud.main_frame.showCombat(data[key]);
                }
                else if (key == "left_combat") {
                    mud.main_frame.closeCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    mud.main_frame.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                    var info = data[key];
                    mud.combat_window.setCombat(info["desc"],
                                                info["timeout"],
                                                info["characters"],
                                                core.data_handler.character_dbref);
                    }
                else if (key == "combat_commands") {
	                mud.combat_window.setCommands(data[key]);
                }
                else if (key == "skill_cd") {
                	var skill_cd = data[key];
                    mud.main_frame.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                }
                else if (key == "skill_cast") {
                    mud.main_frame.setSkillCast(data[key]);
                }
                else if (key == "get_exp") {
                	var get_exp = data[key];
                    mud.main_frame.showGetExp(get_exp["exp"], get_exp["combat"]);
                }
                else if (key == "login") {
                    mud.main_frame.onLogin(data[key]);
                }
                else if (key == "logout") {
                    mud.main_frame.onLogout(data[key]);
                }
                else if (key == "pw_changed") {
                    mud.main_frame.popWindow(password_window);
                }
                else if (key == "unpuppet") {
	                mud.main_frame.onUnpuppet(data[key]);
                }
                else if (key == "char_all") {
                    mud.select_char_window.setCharacters(data[key]);
                }
                else if (key == "max_char") {
                    mud.select_char_window.setMaxNumber(data[key]);
                }
                else if (key == "char_created") {
                    mud.new_char_window.onCharacterCreated(data[key]);
                }
                else if (key == "char_deleted") {
                }
                else if (key == "puppet") {
                    mud.main_frame.onPuppet(data[key]);
                }
                else if (key == "channels") {
                    mud.main_frame.setChannels(data[key])
                }
                else if (key == "shop") {
                    mud.main_frame.showShop(data[key]);
                }
                else if (key == "rankings") {
                	mud.main_frame.setRankings(data[key]);
                }
                else if (key == "in_combat_queue") {
                    mud.main_frame.inCombatQueue(data[key]);
                }
                else if (key == "left_combat_queue") {
                    mud.main_frame.leftCombatQueue(data[key]);
                }
                else if (key == "prepare_match") {
                	mud.main_frame.prepareMatch(data[key]);
                }
                else if (key == "match_rejected") {
                	mud.main_frame.matchRejected(data[key]);
                }
                else if (key == "current_location") {
                    core.map_data.setCurrentLocation(data[key]);
                }
                else if (key == "reveal_map") {
                    core.map_data.revealMap(data[key]);
                }
                else if (key == "revealed_map") {
                    core.map_data.setData(data[key]);
                }
                else {
                    mud.message_window.displayMessage(data[key]);
                }
            }
            catch(error) {
                console.log(key, data[key])
                console.error(error.stack);
            }
        }
    },
}
