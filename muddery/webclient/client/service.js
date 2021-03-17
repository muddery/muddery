
MudderyService = function() {
}

MudderyService.prototype = {

    // commands
    cmdString : function(command, args, context) {
        return JSON.stringify({
            "cmd" : command,
            "args" : args,
            "context": context
        });
    },
    
    sendRawCommand: function(cmd) {
    	Evennia.msg("text", cmd);
    },
    
    // functions when user click a command link
    //
    sendCommandLink: function(cmd, args, context) {
        Evennia.msg("text", this.cmdString(cmd, args, context));
    },
    
    castSkill: function(skill, target) {
        var cmd = "cast_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        Evennia.msg("text", this.cmdString(cmd, args));
    },

    castCombatSkill: function(skill, target) {
        var cmd = "cast_combat_skill";
        var args = {
            "skill": skill,
            "target": target,
        };
        Evennia.msg("text", this.cmdString(cmd, args));
    },

    leaveCombat: function() {
        Evennia.msg("text", this.cmdString("leave_combat", ""));
    },

    doQuickLogin: function(playername) {
        var args = {"playername" : playername};
        Evennia.msg("text", this.cmdString("quick_login", args));
    },

    // login
    login: function(playername, password) {
        var args = {"playername" : playername,
                    "password" : password};
        
        Evennia.msg("text", this.cmdString("connect", args));
    },

    // register
    register: function(playername, password, password_verify, connect) {
        if (password != password_verify) {
            mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
            return;
        }

        var args = {"playername": playername,
                    "password": password,
                    "connect": connect};
        Evennia.msg("text", this.cmdString("create", args));
    },

    // change password
    changePassword: function(current, password, password_verify) {
        if (password != password_verify) {
            mud.main_frame.popupMessage(core.trans("Error"), core.trans("Password does not match."));
            return;
        }

        var args = {"current": current,
                    "new": password};
        Evennia.msg("text", this.cmdString("change_pw", args));
    },

    // create new character
    createCharacter: function(name) {
   	 	var args = {"name": name};
		Evennia.msg("text", this.cmdString("char_create", args));
    },

    // delete a character
    deleteCharacter: function(obj_id) {
        var args = {"id": obj_id};
		Evennia.msg("text", this.cmdString("char_delete", args));
    },
    
    // puppet a character
    puppetCharacter: function(obj_id) {
    	Evennia.msg("text", this.cmdString("puppet", obj_id));
    },
    
    // unpuppet current character
    unpuppetCharacter: function() {
        Evennia.msg("text", this.cmdString("unpuppet", ""));
    },
    
    // look
    look: function(odj_id, context) {
        Evennia.msg("text", this.cmdString("look", odj_id, context));
    },

    inventoryObject: function(position, context) {
        Evennia.msg("text", this.cmdString("inventory_obj", position, context));
    },

    equipmentsObject: function(obj_id, context) {
        Evennia.msg("text", this.cmdString("equipments_obj", obj_id, context));
    },

    // go to
    doGoto : function(odj_id) {
        Evennia.msg("text", this.cmdString("goto", odj_id));
    },
    
    // talk
    doTalk : function(odj_id) {
        Evennia.msg("text", this.cmdString("talk", odj_id));
    },
    
    // buy something
    buyGoods: function(npc, shop, goods) {
    	Evennia.msg("text", this.cmdString("buy", {
    	    npc: npc,
    	    shop: shop,
    	    goods: goods,
    	}));
    },
    
    // dialogue
    finishDialogue: function(dialogue, npc) {
        var args = {"dialogue": dialogue,
                    "npc": npc};
        Evennia.msg("text", this.cmdString("finish_dialogue", args));
    },
    
    // logout
    logout : function() {
        Evennia.msg("text", this.cmdString("quit", ""));
    },
    
    // send command from command box
    doSendCommand: function() {
        var command = $("#box_command :text").val();
        $("#box_command :text").val("");
        
        Evennia.msg("text", command);
    },
    
    // send command text
    doSendText: function(test) {
        Evennia.msg("text", test);
    },
    
    // send out a speech
    say: function(type, target, message) {
        var args = {
            "type": type,
            "target": target,
            "message": message,
        }
        Evennia.msg("text", this.cmdString("say", args));
    },
    
    // make a match
    makeMatch: function() {
    	Evennia.msg("text", this.cmdString("make_match", ""));
    },

    // queue up an honour combat
    queueUpCombat: function() {
    	Evennia.msg("text", this.cmdString("queue_up_combat", ""));
    },
    
    // quit a combat queue
    quitCombatQueue: function() {
    	Evennia.msg("text", this.cmdString("quit_combat_queue", ""));
    },
    
    // confirm an honour combat
    confirmCombat: function() {
    	Evennia.msg("text", this.cmdString("confirm_combat", ""));
    },

    // reject an honour combat
    rejectCombat: function() {
    	Evennia.msg("text", this.cmdString("reject_combat", ""));
    },
    
    // get character rankings
    getRankings: function() {
    	Evennia.msg("text", this.cmdString("get_rankings", ""));
    },

    // query the quest's detail information
    // args:
    //     key: (string) a quest's key
    queryQuest: function(key) {
        Evennia.msg("text", this.cmdString("query_quest", {key: key}));
    },

    // query the skill's detail information
    // args:
    //     key: (string) a skill's key
    querySkill: function(key) {
        Evennia.msg("text", this.cmdString("query_skill", {key: key}));
    },

    // do test
    doTest: function() {
        // test codes
    },
}
