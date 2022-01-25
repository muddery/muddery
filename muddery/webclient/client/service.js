
MudderyService = function() {
}

MudderyService.prototype = {

    // commands
    sendCommand : function(command, args) {
        var data = {
            "cmd" : command,
            "args" : args || "",
        };
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

    // query the unloggedin message
    queryUnloggedIn: function () {
        this.sendCommand("unloggedin_look");
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

    // login
    login: function(username, password) {
        var args = {
            "username" : username,
            "password" : password
        };
        
        this.sendCommand("connect", args);
    },

    // register
    register: function(username, password, password_verify, connect) {
        if (password != password_verify) {
            mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
            return;
        }

        var args = {
            "username": username,
            "password": password,
            "connect": connect
        };
        this.sendCommand("create", args);
    },

    // change password
    changePassword: function(current, password, password_verify) {
        if (password != password_verify) {
            mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
            return;
        }

        var args = {"current": current,
                    "new": password};
        this.sendCommand("change_pw", args);
    },

    // create new character
    createCharacter: function(name) {
   	 	var args = {"name": name};
		this.sendCommand("char_create", args);
    },

    // delete a character
    deleteCharacter: function(obj_id) {
        var args = {"id": obj_id};
		this.sendCommand("char_delete", args);
    },
    
    // puppet a character
    puppetCharacter: function(obj_id) {
    	this.sendCommand("puppet", obj_id);
    },
    
    // unpuppet current character
    unpuppetCharacter: function() {
        this.sendCommand("unpuppet");
    },

    inventoryObject: function(position) {
        this.sendCommand("inventory_obj", position);
    },

    equipmentsObject: function(obj_id) {
        this.sendCommand("equipments_obj", obj_id);
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
    traverse : function(exit_key) {
        this.sendCommand("traverse", exit_key);
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
    
    // logout
    logout : function() {
        this.sendCommand("quit");
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
    say: function(type, target, message) {
        var args = {
            "type": type,
            "target": target,
            "message": message,
        }
        this.sendCommand("say", args);
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
    queryMaps: function (room_list) {
        this.sendCommand("query_maps", {rooms: room_list});
    },

    // do test
    doTest: function() {
        // test codes
    },
}
