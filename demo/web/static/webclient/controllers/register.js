
var _ = parent._;
var parent_controller = parent.controller;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_name").text(_("Name"));
		$("#reg_name").attr("placeholder", _("username"));
		$("#reg_nickname").attr("placeholder", _("nickname"));
		$("#view_password").text(_("Password"));
		$("#reg_password").attr("placeholder", _("password"));
		$("#reg_password_again").attr("placeholder", _("password again"));
		$("#view_register").text(_("Register"));
	},

    // register
    doRegister: function() {
        var playername = $("#reg_name").val();
        var nickname = $("#reg_nickname").val();
        var password = $("#reg_password").val();
        var password_again = $("#reg_password_again").val();

        commands.doRegister(playername, nickname, password, password_again);
        
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

$(document).ready(function() {
	controller.onReady();
});
