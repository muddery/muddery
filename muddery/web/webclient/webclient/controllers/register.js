
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
		$("#view_password").text(_("Password"));
		$("#reg_password").attr("placeholder", _("password"));
		$("#reg_password_verify").attr("placeholder", _("password verify"));
		$("#view_register").text(_("Register"));
	},

    // register
    doRegister: function() {
        var playername = $("#reg_name").val();
        var password = $("#reg_password").val();
        var password_verify = $("#reg_password_verify").val();

        commands.doRegister(playername, password, password_verify, true);
        
        this.clear();
    },
    
    // clear contents
    clear: function() {
        $("#reg_name").val("");
        $("#reg_password").val("");
        $("#reg_password_verify").val("");
    },
};

$(document).ready(function() {
	controller.onReady();
});
