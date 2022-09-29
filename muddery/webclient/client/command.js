
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
    
    // functions when user click a command link
    //
    sendCommandLink: function(cmd, args) {
       this.sendCommand(cmd, args);
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

    castSkill: function(skill, target) {
        var cmd = "cast_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        this.sendCommand(cmd, args);
    },

    castCombatSkill: function(skill, target) {
        var cmd = "cast_combat_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        this.sendCommand(cmd, args);
    },

    leaveCombat: function() {
        this.sendCommand("leave_combat");
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

    queryEquipments: function(callback) {
        this.sendCommand("equipments", {}, callback);
    },

    equipmentsObject: function(obj_id, callback) {
        this.sendCommand("equipments_obj", obj_id, callback);
    },

    // look at an object in the room
    look_room_obj: function(object_key) {
        this.sendCommand("look_room_obj", object_key);
    },

    // look at a character in the room
    // args:
    //  char_id: (int) character's id
    //
    look_room_char: function (char_id) {
        this.sendCommand("look_room_char", char_id);
    },

    // go to
    traverse: function(exit_key, callback) {
        this.sendCommand("traverse", exit_key, callback);
    },
    
    // talk
    doTalk : function(odj_id) {
        this.sendCommand("talk", odj_id);
    },
    
    // buy something
    buyGoods: function(npc, shop, goods) {
    	this.sendCommand("buy", {
    	    npc: npc,
    	    shop: shop,
    	    goods: goods,
    	});
    },
    
    // dialogue
    finishDialogue: function(dialogue, npc) {
        var args = {"dialogue": dialogue,
                    "npc": npc};
        this.sendCommand("finish_dialogue", args);
    },
    
    // send command from command box
    doSendCommand: function() {
        var command = $("#box_command :text").val();
        $("#box_command :text").val("");
        
        this.sendRawCommand(command);
    },
    
    // send command text
    doSendText: function(test) {
        this.sendRawCommand(test);
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
    
    // make a match
    makeMatch: function() {
    	this.sendCommand("make_match");
    },

    // queue up an honour combat
    queueUpCombat: function() {
    	this.sendCommand("queue_up_combat");
    },
    
    // quit a combat queue
    quitCombatQueue: function() {
    	this.sendCommand("quit_combat_queue");
    },
    
    // confirm an honour combat
    confirmCombat: function() {
    	this.sendCommand("confirm_combat");
    },

    // reject an honour combat
    rejectCombat: function() {
    	this.sendCommand("reject_combat");
    },
    
    // get character rankings
    getRankings: function() {
    	this.sendCommand("get_rankings");
    },

    // query the quest's detail information
    // args:
    //     key: (string) a quest's key
    queryQuest: function(key) {
        this.sendCommand("query_quest", {key: key});
    },

    // query the skill's detail information
    // args:
    //     key: (string) a skill's key
    querySkill: function(key) {
        this.sendCommand("query_skill", {key: key});
    },

    // query area maps by a list of room keys
    queryMaps: function (room_list, callback) {
        this.sendCommand("query_maps", {rooms: room_list}, callback);
    },

    // do test
    doTest: function() {
        // test codes
    },
}
