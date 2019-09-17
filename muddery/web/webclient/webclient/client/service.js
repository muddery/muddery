
MudderyService = function() {
}

MudderyService.prototype = {

    // commands
    cmdString : function(command, args) {
        return JSON.stringify({"cmd" : command, "args" : args});
    },
    
    sendRawCommand: function(cmd) {
    	Evennia.msg("text", cmd);
    },
    
    // functions when user click a command link
    //
    sendCommandLink: function(cmd, args) {
        Evennia.msg("text", this.cmdString(cmd, args));
    },
    
    doCastSkill : function(skill, target, combat) {
        var cmd = "castskill";
        var args = {"skill": skill,
                    "target": target,
                    "combat": combat};
        Evennia.msg("text", this.cmdString(cmd, args));
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
            window_main.showAlert(trans("Password does not match."));
            return;
        }

        var args = {"playername": playername,
                    "password": password,
                    "connect": connect};
        Evennia.msg("text", this.cmdString("create", args));
    },

    // change password
    doChangePassword: function(current, password, password_verify) {
        if (password != password_verify) {
            $$.main.showAlert($$.trans("Password does not match."));
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
    doLook : function(dbref) {
        Evennia.msg("text", this.cmdString("look", dbref));
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
    doDialogue: function(dialogue, sentence, npc) {
        if ($$.data_handler.dialogues_list.length > 0) {
            $$.main.showDialogue($$.data_handler.dialogues_list.shift());
        }
        else {
            var args = {"dialogue": dialogue,
                        "sentence": sentence,
                        "npc": npc};
            Evennia.msg("text", this.cmdString("dialogue", args));
        }
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
    say: function(channel, message) {
        var args = {"channel": channel,
                    "message": message}
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
