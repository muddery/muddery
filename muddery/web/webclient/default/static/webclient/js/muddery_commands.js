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
    
    // functions when user click a button
    // login
    doLogin : function() {
        var playername = $("#page_login :text").val();
        var password = $("#page_login :password").val();
        $("#page_login :password").val("");
        
        var args = {"playername" : playername,
                    "password" : password};
        sendCommand(this.cmdString("connect", args));
    },

    // register
    doRegister : function() {
        var playername = $("#page_login :text").val();
        var password = $("#page_login :password").val();
        $("#page_login :password").val("");

        var args = {"playername" : playername,
                    "password" : password};
        sendCommand(this.cmdString("create_connect", args));
    },
    
    // look
    doLook : function(object) {
        sendCommand(this.cmdString("look", object));
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
