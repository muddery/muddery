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
    doLogin: function(playername, password) {
        var args = {"playername" : playername,
                    "password" : password};
        Evennia.msg("text", this.cmdString("connect", args));
    },

    // register
    doRegister: function(playername, nickname, password) {
        if (!Evennia.isConnected()) {
            Evennia.connect();
        }

        // $("#login_name").val(playername);
        //if (password != password_again) {
        //    webclient.displayAlert(LS("Password does not match."));
        //    return;
        //}

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
        }
        else {
            var args = {"dialogue": $(caller).attr("dialogue"),
                        "sentence": $(caller).attr("sentence")};

            var npc = $(caller).attr("npc");
            if (npc) {
                args["npc"] = npc;
            }
            Evennia.msg("text", this.cmdString("dialogue", args));
        }
    },

    // shop goods detail
    doShopGoodsLink: function(obj_dbref) {
        var goods_list = data_handler.shop_data["goods"];
        for (var i in goods_list) {
            if (obj_dbref == goods_list[i]["dbref"]) {
                popupmgr.showGoods(goods_list[i]);
                break;
            }
        }
    },
    
    // logout
    doLogout : function() {
        $.cookie("is_auto_login", '', {expires: -1});
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
    doSay: function() {
        var speech = $("#box_speech :text").val();
        $("#box_speech :text").val("");

        if (!speech) {
            return;
        }

        Evennia.msg("text", this.cmdString("say", speech));
    },
    
    // do test
    doTest : function() {
        // test codes
    },

    doAutoLoginConfig: function(playername, password, save_password, auto_login) {
        if (save_password) {
            $.cookie("login_name", playername);
            $.cookie("login_password", password);

            if (auto_login) {
                $.cookie("is_auto_login", 'true');
            } else {
                $.cookie("is_auto_login", '', {expires: -1});
            }
        }
    },

    doSetSavePassword: function(save_password) {
        if (save_password) {
            $.cookie("is_save_password", 'true');
        } else {
            $.cookie("login_name", '', {expires: -1});
            $.cookie("login_password", '', {expires: -1});
            $.cookie("is_save_password", '', {expires: -1});
            $.cookie("is_auto_login", '', {expires: -1});
        }
    },
}
