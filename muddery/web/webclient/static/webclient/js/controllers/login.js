
var login = {

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

    doSetSavePassword: function() {
        var save_password = $("#cb_save_password").is(":checked");
        parent.commands.doSetSavePassword(save_password);

        if (!save_password) {
            $("#cb_auto_login").removeAttr("checked");
        }
    },
};
