
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
        Evennia.emitter.on("text", mudcore.client.onText);
        //Evennia.emitter.on("prompt", onPrompt);
        //Evennia.emitter.on("default", onDefault);
        Evennia.emitter.on("connection_close", main_window.onConnectionClose);
        // silence currently unused events
        Evennia.emitter.on("connection_open", main_window.onConnectionOpen);
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
            main_window.showAlert(mudcore.trans("Can not connect to the server."));
            return;
        }
    },

 	onText: function(args, kwargs) {
 	    for (var i = 0; i < args.length; i++) {
 		    mudcore.client.doShow("out", args[i]);
 		}
 	},
 	
    doShow: function(type, msg) {
        var data = null;
        
        if (type == "out") {
            try {
                var decode = JSON.parse(msg);
                var type = Object.prototype.toString.call(decode);
                
                if (type == "[object Object]") {
                    // Json object.
                    data = decode;
                }
                else if (type == "[object String]") {
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
                    
        this.displayData(data);
    },

    // display all kinds of data
    displayData : function(data) {
        for (var key in data) {
            try {
                log(key, data[key]);

                if (key == "settings") {
                    main_window.setClient(data[key]);
                }
                else if (key == "msg") {
                	var msg = mudcore.text2html.parseHtml(data[key]);
                    message_window.displayMessage(msg);
                }
                else if (key == "alert") {
              		main_window.showAlert(data[key]);
                }
                else if (key == "out") {
                    message_window.displayMessage(data[key], "out");
                }
                else if (key == "err") {
                    message_window.displayMessage(data[key]);
                }
                else if (key == "sys") {
                    message_window.displayMessage(data[key], "sys");
                }
                else if (key == "debug") {
                	message_window.displayMessage(data[key], "debug");
                }
                else if (key == "prompt") {
                	message_window.displayMessage(data[key], "prompt");
                }
                else if (key == "look_around") {
                    scene_window.setScene(data[key]);
                }
                else if (key == "obj_moved_in") {
                    main_window.showObjMovedIn(data[key]);
                }
                else if (key == "obj_moved_out") {
                    main_window.showObjMovedOut(data[key]);
                }
                else if (key == "player_online") {
                    main_window.showPlayerOnline(data[key]);
                }
                else if (key == "player_offline") {
                    main_window.showPlayerOffline(data[key]);
                }
                else if (key == "look_obj") {
        			popup_object.setObject(data[key]);
        			popup_object.show();
                }
                else if (key == "dialogue") {
                    popup_dialogue.setDialogue(data[key], mudcore.data_handler.getEscapes());
                    if (popup_dialogue.hasDialogue() && !main_window.isWindowShow(combat_window)) {
                        popup_dialogue.show();
                    }
                }
                else if (key == "status") {
                    var status = data[key];
                    main_window.setStatus(status);
                }
                else if (key == "equipments") {
			        char_data_window.setEquipments(data[key]);
                }
                else if (key == "inventory") {
                    inventory_window.setInventory(data[key]);
                }
                else if (key == "skills") {
                    mudcore.data_handler.setSkills(data[key]);
                    skills_window.setSkills(data[key]);
                }
                else if (key == "quests") {
                	quests_window.setQuests(data[key]);
                }
                else if (key == "get_objects") {
                	var get_objects = data[key];
                    main_window.showGetObjects(get_objects["accepted"], get_objects["rejected"]);
                }
                else if (key == "joined_combat") {
                    main_window.showCombat(data[key]);
                }
                else if (key == "left_combat") {
                    main_window.closeCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    main_window.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                    var info = data[key];
                    combat_window.setCombat(info["desc"],
                                            info["timeout"],
                                            info["characters"],
                                            mudcore.data_handler.character_dbref);
                }
                else if (key == "combat_commands") {
	                combat_window.setCommands(data[key]);
                }
                else if (key == "skill_cd") {
                	var skill_cd = data[key];
                    main_window.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                }
                else if (key == "skill_cast") {
                    main_window.setSkillCast(data[key]);
                }
                else if (key == "get_exp") {
                	var get_exp = data[key];
                    main_window.showGetExp(get_exp["exp"], get_exp["combat"]);
                }
                else if (key == "login") {
                    main_window.onLogin(data[key]);
                }
                else if (key == "logout") {
                    main_window.onLogout(data[key]);
                }
                else if (key == "pw_changed") {
                    main_window.popWindow(password_window);
                }
                else if (key == "unpuppet") {
	                main_window.onUnpuppet(data[key]);
                }
                else if (key == "char_all") {
                    select_char_window.setCharacters(data[key]);
                }
                else if (key == "char_created") {
                    new_char_window.onCharacterCreated(data[key]);
                }
                else if (key == "char_deleted") {
                }
                else if (key == "puppet") {
                    main_window.onPuppet(data[key]);
                }
                else if (key == "channels") {
                    main_window.setChannels(data[key])
                }
                else if (key == "shop") {
                    main_window.showShop(data[key]);
                }
                else if (key == "rankings") {
                	main_window.setRankings(data[key]);
                }
                else if (key == "in_combat_queue") {
                    main_window.inCombatQueue(data[key]);
                }
                else if (key == "left_combat_queue") {
                    main_window.leftCombatQueue(data[key]);
                }
                else if (key == "prepare_match") {
                	main_window.prepareMatch(data[key]);
                }
                else if (key == "match_rejected") {
                	main_window.matchRejected(data[key]);
                }
                else if (key == "current_location") {
                    mudcore.map_data.setCurrentLocation(data[key]);
                }
                else if (key == "reveal_map") {
                    mudcore.map_data.revealMap(data[key]);
                }
                else if (key == "revealed_map") {
                    mudcore.map_data.setData(data[key]);
                }
                else {
                    message_window.displayMessage(data[key]);
                }
            }
            catch(error) {
                console.log(key, data[key])
                console.error(error.stack);
            }
        }
    },
}
