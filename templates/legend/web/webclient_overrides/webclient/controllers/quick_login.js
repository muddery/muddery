
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
		$("#view_header").text(_("Please input your name."));
		$("#login_name").attr("placeholder", _("name"));
		$("#view_button_login").text(_("Login"));
	},
	
    // login
    doLogin: function() {
        var playername = $("#login_name").val();
        commands.doQuickLogin(playername);
    },
};

$(document).ready(function() {
	controller.onReady();
});