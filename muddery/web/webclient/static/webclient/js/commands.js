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
        Evennia.msg("text", this.cmdString(cmd, args));
    },
    
    doCastSkill : function(skill) {
        if (skill in data_handler.skill_cd_time) {
            var cd_time = data_handler.skill_cd_time[skill];
            var current_time = (new Date()).valueOf();
            if (cd_time > current_time) {
                return;
            }
        }

        var cmd = "castskill";
        var args = {"skill": skill,
                    "target": data_handler.current_target};
        Evennia.msg("text", this.cmdString(cmd, args));
    },
    
    
    // functions when user click a button

    // login
    doLogin : function() {
        var playername = $("#login_name").val();
        var password = $("#login_password").val();

        $("#login_password").val("");
        $("#reg_password").val("");
        $("#reg_password_again").val("");

        var args = {"playername" : playername,
                    "password" : password};
        Evennia.msg("text", this.cmdString("connect", args));

        commands.doAutoLoginConfig(playername, password);
    },

    // register
    doRegister : function() {
        if (!Evennia.isConnected()) {
            Evennia.connect();
        }
        
        var playername = $("#reg_name").val();
        var nickname = $("#reg_nickname").val();
        var password = $("#reg_password").val();
        var password_again = $("#reg_password_again").val();

        $("#login_name").val(playername);
        $("#login_password").val("");
        $("#reg_password").val("");
        $("#reg_password_again").val("");

        if (password != password_again) {
            webclient.displayAlert(LS("Password does not match."));
            return;
        }

        var args = {"playername" : playername,
                    "nickname" : nickname,
                    "password" : password};
        Evennia.msg("text", this.cmdString("create_connect", args));
    },
    
    // look
    doLook : function(object) {
        Evennia.msg("text", this.cmdString("look", object));
    },
    
    // talk
    doTalk : function(object) {
        Evennia.msg("text", this.cmdString("talk", object));
    },
    
    // dialogue
    doDialogue : function(caller) {
        if(data_handler.dialogues_list.length > 0) {
            popupmgr.showDialogue(data_handler.dialogues_list.shift());
        } else {
            var args = {"dialogue": $(caller).attr("dialogue"),
                        "sentence": $(caller).attr("sentence")};

            var npc = $(caller).attr("npc");
            if (npc) {
                args["npc"] = npc;
            }
            Evennia.msg("text", this.cmdString("dialogue", args));
        }
    },
    
    // logout
    doLogout : function() {
        $.cookie("is_auto_login", '', {expires: -1});
        Evennia.msg("text", this.cmdString("quit", ""));
    },
    
    // common command
    doSendCommand: function() {
        var command = $("#box_command :text").val();
        $("#box_command :text").val("");
        
        sendCommand(command);
    },
    
    // do test
    doTest : function() {
        // test codes
    },

    doAutoLoginConfig : function(playername, password) {
        if($("#cb_save_password").is(":checked")) {
            $.cookie("login_name", playername);
            $.cookie("login_password", password);

            if($("#cb_auto_login").is(":checked")) {
                $.cookie("is_auto_login", 'true');
            } else {
                $.cookie("is_auto_login", '', {expires: -1});
            }
        }
    },

    doSetSavePassword : function() {
        if($("#cb_save_password").is(":checked")) {
            $.cookie("is_save_password", 'true');
        } else {
            $.cookie("login_name", '', {expires: -1});
            $.cookie("login_password", '', {expires: -1});
            $.cookie("is_save_password", '', {expires: -1});
            $.cookie("is_auto_login", '', {expires: -1});
            $("#cb_auto_login").removeAttr("checked");
        }
    },
}


// Callback function - called when the browser window resizes
$(window).resize(webclient.doSetSizes);
