/*
Muddery webclient (javascript component)
*/

var commands = {
    // commands
    cmdString : function(command, args) {
        return JSON.stringify({"cmd" : command, "args" : args});
    },
    
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
    doLook : function() {
        sendCommand(this.cmdString("look", ""));
    },
    
    // quit
    doQuit : function() {
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
        this.showAlert("test", "btn");
    }
}


// Callback function - called when the browser window resizes
$(window).resize(webclient.doSetSizes);
