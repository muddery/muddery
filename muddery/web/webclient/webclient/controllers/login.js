
var controller = {

    // login
    doLogin: function() {
        var playername = $("#login_name").val();
        var password = $("#login_password").val();
        var save_password = $("#cb_save_password").is(":checked");
        var auto_login = $("#cb_auto_login").is(":checked");

        $("#login_password").val("");

        parent.commands.doLogin(playername, password);
        parent.commands.doAutoLoginConfig(playername, password, save_password, auto_login);
    },

    doSavePassword: function() {
        var save_password = $("#cb_save_password").is(":checked");
        parent.commands.doSavePassword(save_password);

        if (!save_password) {
            $("#cb_auto_login").removeAttr("checked");
        }
    },
    
    setPlayerName: function(playername) {
    	$("#login_name").val(playername);
    	$("#login_password").val("");
    },
};
