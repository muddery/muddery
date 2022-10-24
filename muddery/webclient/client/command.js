
MudderyCommand = function() {
}

MudderyCommand.prototype = {
    // unique request serial number
    serial_number: 0,

    // callback functions
    callbacks: {},

    // commands
    sendCommand : function(command, args, callback) {
        var data = {
            "cmd": command,
            "args": args || "",
        };
        if (callback && typeof(callback) == "function") {
            var sn = this.serial_number++;
            this.callbacks[sn] = callback;
            data["sn"] = sn;
        }
        Connection.send(JSON.stringify(data));
    },
    
    sendRawCommand: function(text) {
    	Connection.send(text);
    },

    respond: function(sn, code, data, msg) {
        var callback = this.callbacks[sn];
        if (callback) {
            delete this.callbacks[sn];
            callback(code, data, msg);
        }
    },

    // query necessary data when the client connect to the server
    firstConnect: function(callback) {
        this.sendCommand("first_connect", {}, callback);
    },

    // register
    register: function(username, password, connect, callback) {
        var args = {
            "username": username,
            "password": settings.enable_encrypt? core.crypto.encrypt(password): password,
            "connect": connect
        };
        this.sendCommand("create_account", args, callback);
    },

    // login
    login: function(username, password, callback) {
        var args = {
            "username" : username,
            "password" : settings.enable_encrypt? core.crypto.encrypt(password): password,
        };

        this.sendCommand("login", args, callback);
    },

    // logout
    logout : function(callback) {
        this.sendCommand("logout", {}, callback);
    },

    // get a player's all available characters
    queryAllCharacters : function(callback) {
        this.sendCommand("char_all", {}, callback);
    },

    castSkill: function(skill, target, callback) {
        var cmd = "cast_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        this.sendCommand(cmd, args, callback);
    },

    castCombatSkill: function(skill, target, callback) {
        var cmd = "cast_combat_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        this.sendCommand(cmd, args, callback);
    },

    leaveCombat: function(callback) {
        this.sendCommand("leave_combat", {}, callback);
    },

    // change password
    changePassword: function(current, new_password, callback) {
        var args = {
            "current": settings.enable_encrypt? core.crypto.encrypt(current): current,
            "new": settings.enable_encrypt? core.crypto.encrypt(new_password): new_password,
        };
        this.sendCommand("change_pw", args, callback);
    },

    // create new character
    createCharacter: function(name, callback) {
   	 	var args = {"name": name};
		this.sendCommand("char_create", args, callback);
    },

    // delete a character
    deleteCharacter: function(obj_id, callback) {
        var args = {"id": obj_id};
		this.sendCommand("char_delete", args, callback);
    },
    
    // puppet a character
    puppetCharacter: function(obj_id, callback) {
    	this.sendCommand("puppet", obj_id, callback);
    },
    
    // unpuppet current character
    unpuppetCharacter: function(callback) {
        this.sendCommand("unpuppet", {}, callback);
    },

    queryInventory: function(callback) {
        this.sendCommand("inventory", {}, callback);
    },

    inventoryObject: function(position, callback) {
        this.sendCommand("inventory_obj", position, callback);
    },

    equip: function(callback) {
        this.sendCommand("equip", {}, callback);
    },

    queryEquipments: function(callback) {
        this.sendCommand("all_equipments", {}, callback);
    },

    equipmentsObject: function(obj_id, callback) {
        this.sendCommand("equipments_obj", obj_id, callback);
    },

    // look at an object in the room
    lookRoomObj: function(object_key, callback) {
        this.sendCommand("look_room_obj", object_key, callback);
    },

    // look at a character in the room
    // args:
    //  char_id: (int) character's id
    //
    lookRoomChar: function (char_id, callback) {
        this.sendCommand("look_room_char", char_id, callback);
    },

    // go to
    traverse: function(exit_key, callback) {
        this.sendCommand("traverse", exit_key, callback);
    },
    
    // talk
    talk : function(odj_id, callback) {
        this.sendCommand("talk", odj_id, callback);
    },
    
    // buy something
    buy: function(npc, shop, goods, callback) {
    	this.sendCommand("buy", {
    	    npc: npc,
    	    shop: shop,
    	    goods: goods,
    	}, callback);
    },
    
    // dialogue
    finishDialogue: function(dialogue, npc, callback) {
        var args = {
            "dialogue": dialogue,
            "npc": npc
        };
        this.sendCommand("finish_dialogue", args, callback);
    },
    
    // send out a speech
    say: function(type, target, message, callback) {
        var args = {
            "type": type,
            "target": target,
            "message": message,
        }
        this.sendCommand("say", args, callback);
    },

    // queue up an honour combat
    queueUpCombat: function(callback) {
    	this.sendCommand("queue_up_combat", {}, callback);
    },
    
    // quit a combat queue
    quitCombatQueue: function(callback) {
    	this.sendCommand("quit_combat_queue", {}, callback);
    },
    
    // confirm an honour combat
    confirmCombat: function(callback) {
    	this.sendCommand("confirm_combat", {}, callback);
    },

    // reject an honour combat
    rejectCombat: function(callback) {
    	this.sendCommand("reject_combat", {}, callback);
    },
    
    // get character rankings
    getRankings: function(callback) {
    	this.sendCommand("get_rankings", {}, callback);
    },

    // query the player's all quests
    queryAllQuests: function(callback) {
        this.sendCommand("all_quests", {}, callback);
    },

    // query the quest's detail information
    // args:
    //     key: (string) a quest's key
    queryQuest: function(key, callback) {
        this.sendCommand("query_quest", {key: key}, callback);
    },

    // query the player's all skills
    queryAllSkills: function(callback) {
        this.sendCommand("all_skills", {}, callback);
    },

    // query the skill's detail information
    // args:
    //     key: (string) a skill's key
    querySkill: function(key, callback) {
        this.sendCommand("query_skill", {key: key}, callback);
    },

    // query the game world's map
    queryMap: function (callback) {
        this.sendCommand("query_map", {}, callback);
    },

    // do test
    doTest: function() {
        // test codes
    },
}
