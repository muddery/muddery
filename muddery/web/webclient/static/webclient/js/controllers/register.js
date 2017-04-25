
var register = {

    // register
    doRegister : function() {
        var playername = $("#reg_name").val();
        var nickname = $("#reg_nickname").val();
        var password = $("#reg_password").val();
        var password_again = $("#reg_password_again").val();

        $("#login_password").val("");
        $("#reg_password").val("");
        $("#reg_password_again").val("");

        if (password != password_again) {
            parent.webclient.displayAlert(LS("Password does not match."));
            return;
        }

        parent.commands.doRegister(playername, nickname, password);
    },
};