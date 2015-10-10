/*
Muddery webclient (javascript component)
*/

var commands = {
    // commands
    cmdString : function(command, args) {
        return JSON.stringify({"cmd" : command, "args" : args});
    },
    
    // functions when user click a command link
    //
    doCommandLink : function(caller) {
        var cmd = $(caller).attr("cmd_name");
        var args = $(caller).attr("cmd_args");
        sendCommand(this.cmdString(cmd, args));
    },
    
    doCombatSkill : function(caller) {
        var cmd = "combat_skill";
        var args = {"skill": $(caller).attr("key"),
                    "target": combat.get_current_target()};
        sendCommand(this.cmdString(cmd, args));
    },
    
    // functions when user click a button
    // login
    doLogin : function() {
        var playername = $("#login_name").val();
        var password = $("#login_password").val();
        $("#login_password").val("");
        
        var args = {"playername" : playername,
                    "password" : password};
        sendCommand(this.cmdString("connect", args));
    },

    // register
    doRegister : function() {
        var playername = $("#reg_name").val();
        var nickname = $("#reg_nickname").val();
        var password = $("#reg_password").val();
        $("#reg_password").val("");

        var args = {"playername" : playername,
                    "nickname" : nickname,
                    "password" : password};
        sendCommand(this.cmdString("create_connect", args));
    },
    
    // look
    doLook : function(object) {
        sendCommand(this.cmdString("look", object));
    },
    
    // talk
    doTalk : function(object) {
        sendCommand(this.cmdString("talk", object));
    },
    
    // dialogue
    doDialogue : function(caller) {
        var args = {"dialogue": $(caller).attr("dialogue"),
                    "sentence": $(caller).attr("sentence")};
                    
        var npc = $(caller).attr("npc");
        if (npc) {
            args["npc"] = npc;
        }
        sendCommand(this.cmdString("dialogue", args));
    },
    
    // logout
    doLogout : function() {
        sendCommand(this.cmdString("quit", ""));
    },
    
    // common command
    doSendCommand : function() {
        var command = $("#page_command :text").val();
        $("#page_command :text").val("");
        
        sendCommand(command);
    },
    
    // do test
    doTest : function() {
        // test codes
    }
}


// Callback function - called when the browser window resizes
$(window).resize(webclient.doSetSizes);
