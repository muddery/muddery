
var _ = parent._;
var parent_controller = parent.controller;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_header").text(_("Please login."));
		$("#login_name").attr("placeholder", _("username"));
		$("#login_password").attr("placeholder", _("password"));
		$("#view_save_password").text(_("Save Password"));
		$("#view_auto_login").text(_("Auto Login"));
		$("#view_button_login").text(_("Login"));
	},
	
    // login
    doLogin: function() {
        var playername = $("#login_name").val();
        var password = $("#login_password").val();
        var save_password = $("#cb_save_password").is(":checked");
        var auto_login = $("#cb_auto_login").is(":checked");

        $("#login_password").val("");

        commands.doLogin(playername, password);
        commands.doAutoLoginConfig(playername, password, save_password, auto_login);
    },

    doSavePassword: function() {
        var save_password = $("#cb_save_password").is(":checked");
        commands.doSavePassword(save_password);

        if (!save_password) {
            $("#cb_auto_login").removeAttr("checked");
        }
    },
    
    setPlayerName: function(playername) {
    	$("#login_name").val(playername);
    	$("#login_password").val("");
    },
};

$(document).ready(function() {
	controller.onReady();
});