
if (typeof(require) != "undefined") {
    require("../client/evennia.js");
    require("../client/defines.js");
}

$$.client = {
 	onText: function(args, kwargs) {
 	    for (index in args) {
 		    $$.client.doShow("out", args[index]);
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
                if (key == "settings") {
                    $$.main.setClient(data[key]);
                }
                else if (key == "msg") {
                	var msg = $$.text2html.parseHtml(data[key]);
                    $$.main.displayMsg(msg);
                }
                else if (key == "alert") {
              		$$.main.showAlert(data[key]);
                }
                else if (key == "out") {
                    $$.main.displayMsg(data[key], "out");
                }
                else if (key == "err") {
                    $$.main.displayMsg(data[key]);
                }
                else if (key == "sys") {
                    $$.main.displayMsg(data[key], "sys");
                }
                else if (key == "debug") {
                	$$.main.displayMsg(data[key], "debug");
                }
                else if (key == "prompt") {
                	$$.main.displayMsg(data[key], "prompt");
                }
                else if (key == "look_around") {
                    $$.main.setScene(data[key]);
                }
                else if (key == "obj_moved_in") {
                    $$.main.showObjMovedIn(data[key]);
                }
                else if (key == "obj_moved_out") {
                    $$.main.showObjMovedOut(data[key]);
                }
                else if (key == "player_online") {
                    $$.main.showPlayerOnline(data[key]);
                }
                else if (key == "player_offline") {
                    $$.main.showPlayerOffline(data[key]);
                }
                else if (key == "look_obj") {
                    var obj = data[key];
        			$$.main.showObject(obj["dbref"],
        								  obj["name"],
        								  obj["icon"],
        								  obj["desc"],
        								  obj["cmds"]);
                }
                else if (key == "dialogues_list") {
                    $$.main.setDialogueList(data[key]);
                }
                else if (key == "status") {
                    var status = data[key];
                    $$.main.setStatus(status);
                }
                else if (key == "equipments") {
			        $$.main.setEquipments(data[key]);
                }
                else if (key == "inventory") {
                    $$.main.setInventory(data[key]);
                }
                else if (key == "skills") {
                    $$.main.setSkills(data[key]);
                }
                else if (key == "quests") {
                	$$.main.setQuests(data[key]);
                }
                else if (key == "get_objects") {
                	var get_objects = data[key];
                    $$.main.showGetObjects(get_objects["accepted"], get_objects["rejected"], get_objects["combat"]);
                }
                else if (key == "joined_combat") {
                    $$.main.showCombat(data[key]);
                }
                else if (key == "left_combat") {
                    $$.main.closeCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    $$.main.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                    $$.main.setCombatInfo(data[key]);
                }
                else if (key == "combat_commands") {
                    $$.main.setCombatCommands(data[key]);
                }
                else if (key == "skill_cd") {
                	var skill_cd = data[key];
                    $$.main.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                }
                else if (key == "skill_cast") {
                    $$.main.setSkillCast(data[key]);
                }
                else if (key == "get_exp") {
                	var get_exp = data[key];
                    $$.main.showGetExp(get_exp["exp"], get_exp["combat"]);
                }
                else if (key == "login") {
                    $$.main.onLogin(data[key]);
                }
                else if (key == "logout") {
                    $$.main.onLogout(data[key]);
                }
                else if (key == "unpuppet") {
	                $$.main.onUnpuppet(data[key]);
                }
                else if (key == "char_all") {
                    $$.main.setAllCharacters(data[key]);
                }
                else if (key == "char_created") {
                    $$.main.onCharacterCreated(data[key]);
                }
                else if (key == "char_deleted") {
                    $$.main.onCharacterDeleted(data[key]);
                }
                else if (key == "puppet") {
                    $$.main.onPuppet(data[key]);
                }
                else if (key == "channels") {
                    $$.main.setChannels(data[key])
                }
                else if (key == "shop") {
                	var shop = data[key];
                    $$.main.showShop(shop["name"],
                    		 			shop["icon"],
                    		 			shop["desc"],
                    		 			shop["goods"]);
                }
                else if (key == "rankings") {
                	$$.main.setRankings(data[key]);
                }
                else if (key == "in_combat_queue") {
                    $$.main.inCombatQueue(data[key]);
                }
                else if (key == "left_combat_queue") {
                    $$.main.leftCombatQueue(data[key]);
                }
                else if (key == "prepare_match") {
                	$$.main.prepareMatch(data[key]);
                }
                else if (key == "match_rejected") {
                	$$.main.matchRejected(data[key]);
                }
                else if (key == "current_location") {
                    $$.map_data.setCurrentLocation(data[key]);
                }
                else if (key == "reveal_map") {
                    $$.map_data.revealMap(data[key]);
                }
                else if (key == "revealed_map") {
                    $$.map_data.setData(data[key]);
                }
                else {
                    $$.main.displayMsg(data[key]);
                }
            }
            catch(error) {
                console.log(key, data[key])
                console.error(error.stack);
            }
        }
    },

    // Event when client finishes loading
    onReady: function() {
        // This is safe to call, it will always only
        // initialize once.
        Evennia.init();

        // register listeners
        Evennia.emitter.on("text", $$.client.onText);
        //Evennia.emitter.on("prompt", onPrompt);
        //Evennia.emitter.on("default", onDefault);
        Evennia.emitter.on("connection_close", $$.main.onConnectionClose);
        // silence currently unused events
        Evennia.emitter.on("connection_open", $$.main.onConnectionOpen);
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
            $$.main.showAlert("Can not connect to the server.");
            return;
        }
    },
}

// Input jQuery callbacks
//$(document).unbind("keydown");

// Callback function - called when the browser window resizes
//$(window).unbind("resize");
//$(window).resize($$.main.doSetSizes);


