
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
    deleteCharacter: function(dbref) {
        var args = {"dbref": dbref};
		Evennia.msg("text", this.cmdString("char_delete", args));
    },
    
    // puppet a character
    puppetCharacter: function(dbref) {
    	Evennia.msg("text", this.cmdString("puppet", dbref));
    },
    
    // unpuppet current character
    unpuppetCharacter: function() {
        Evennia.msg("text", this.cmdString("unpuppet", ""));
    },
    
    // look
    look: function(dbref, context) {
        Evennia.msg("text", this.cmdString("look", dbref, context));
    },

    inventoryObject: function(dbref, context) {
        Evennia.msg("text", this.cmdString("inventory_obj", dbref, context));
    },

    // go to
    doGoto : function(dbref) {
        Evennia.msg("text", this.cmdString("goto", dbref));
    },
    
    // talk
    doTalk : function(dbref) {
        Evennia.msg("text", this.cmdString("talk", dbref));
    },
    
    // buy something
    buyGoods: function(dbref) {
    	Evennia.msg("text", this.cmdString("buy", dbref));
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
    
    // do test
    doTest: function() {
        // test codes
    },
}
