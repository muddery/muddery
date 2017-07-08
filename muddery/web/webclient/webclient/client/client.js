/*
Muddery webclient (javascript component)
*/

var client = {
 	onText: function(args, kwargs) {
 	    for (index in args) {
 		    client.doShow("out", args[index]);
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
                    controller.setClient(data[key]);
                }
                else if (key == "msg") {
                	var msg = text2html.parseHtml(data[key]);
                    controller.displayMsg(msg);
                }
                else if (key == "alert") {
              		controller.showAlert(data[key]);
                }
                else if (key == "out") {
                    controller.displayMsg(data[key], "out");
                }
                else if (key == "err") {
                    controller.displayMsg(data[key]);
                }
                else if (key == "sys") {
                    controller.displayMsg(data[key], "sys");
                }
                else if (key == "debug") {
                	controller.displayMsg(data[key], "debug");
                }
                else if (key == "prompt") {
                	controller.displayMsg(data[key], "prompt");
                }
                else if (key == "look_around") {
                    controller.setScene(data[key]);
                }
                else if (key == "obj_moved_in") {
                    controller.showObjMovedIn(data[key]);
                }
                else if (key == "obj_moved_out") {
                    controller.showObjMovedOut(data[key]);
                }
                else if (key == "player_online") {
                    controller.showPlayerOnline(data[key]);
                }
                else if (key == "player_offline") {
                    controller.showPlayerOffline(data[key]);
                }
                else if (key == "look_obj") {
                    var obj = data[key];
        			controller.showObject(obj["dbref"],
        								  obj["name"],
        								  obj["icon"],
        								  obj["desc"],
        								  obj["cmds"]);
                }
                else if (key == "dialogues_list") {
                    controller.setDialogueList(data[key]);
                }
                else if (key == "status") {
                    var status = data[key];
                    controller.setStatus(status);
                }
                else if (key == "equipments") {
			        controller.setEquipments(data[key]);
                }
                else if (key == "inventory") {
                    controller.setInventory(data[key]);
                }
                else if (key == "skills") {
                    controller.setSkills(data[key]);
                }
                else if (key == "quests") {
                	controller.setQuests(data[key]);
                }
                else if (key == "get_objects") {
                	var get_objects = data[key];
                    controller.showGetObjects(get_objects["accepted"], get_objects["rejected"], get_objects["combat"]);
                }
                else if (key == "joined_combat") {
                    controller.showCombat(data[key]);
                }
                else if (key == "left_combat") {
                    controller.closeCombat(data[key]);
                }
                else if (key == "combat_finish") {
                    controller.finishCombat(data[key]);
                }
                else if (key == "combat_info") {
                	var info = data[key];
                    controller.setCombatInfo(info["desc"], info["characters"]);
                }
                else if (key == "combat_commands") {
                    controller.setCombatCommands(data[key]);
                }
                else if (key == "skill_cd") {
                	var skill_cd = data[key];
                    controller.setSkillCD(skill_cd["skill"], skill_cd["cd"], skill_cd["gcd"]);
                }
                else if (key == "skill_result") {
                    controller.setSkillResult(data[key]);
                }
                else if (key == "get_exp") {
                	var get_exp = data[key];
                    controller.showGetExp(get_exp["exp"], get_exp["combat"]);
                }
                else if (key == "login") {
                    controller.onLogin(data[key]);
                }
                else if (key == "logout") {
                    controller.onLogout(data[key]);
                }
                else if (key == "puppet") {
                    controller.onPuppet(data[key]);
                }
                else if (key == "channels") {
                    controller.setChannels(data[key])
                }
                else if (key == "shop") {
                	var shop = data[key];
                    controller.showShop(shop["name"],
                    		 			shop["icon"],
                    		 			shop["desc"],
                    		 			shop["goods"]);
                }
                else if (key == "current_location") {
                    map_data.setCurrentLocation(data[key]);
                }
                else if (key == "reveal_map") {
                    map_data.revealMap(data[key]);
                }
                else if (key == "revealed_map") {
                    map_data.setData(data[key]);
                }
                else {
                    controller.displayMsg(data[key]);
                }
            }
            catch(error) {
                console.log(key, data[key])
                console.error(error.message);
            }
        }
    },
}

// Input jQuery callbacks
//$(document).unbind("keydown");

// Callback function - called when the browser window resizes
//$(window).unbind("resize");
//$(window).resize(controller.doSetSizes);

// Event when client finishes loading
$(document).ready(function() {

    local_string.setLanguage(settings.default_language);

	controller.onReady();

    // Event when client window changes
    $(window).bind("resize", controller.doSetSizes);
});

$(window).load(function() {
    // It is called

    // This is safe to call, it will always only
    // initialize once.
    Evennia.init();

    // register listeners
    Evennia.emitter.on("text", client.onText);
    //Evennia.emitter.on("prompt", onPrompt);
    //Evennia.emitter.on("default", onDefault);
    Evennia.emitter.on("connection_close", controller.onConnectionClose);
    // silence currently unused events
    Evennia.emitter.on("connection_open", controller.onConnectionOpen);
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
});
