
var controller = {

    // register
    doRegister: function() {
        var playername = $("#reg_name").val();
        var nickname = $("#reg_nickname").val();
        var password = $("#reg_password").val();
        var password_again = $("#reg_password_again").val();

        parent.commands.doRegister(playername, nickname, password, password_again);
        
        this.clear();
    },
    
    // clear contents
    clear: function() {
        $("#reg_name").val("");
        $("#reg_nickname").val("");
        $("#reg_password").val("");
        $("#reg_password_again").val("");
    },
};