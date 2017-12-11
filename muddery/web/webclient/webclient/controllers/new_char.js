
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
	// on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_header").text(_("Set Character"));
		$("#view_name").text(_("Name"));
		$("#button_create").text(_("Create"));
		$("#char_name").attr("placeholder", _("name"));
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

    createCharacter: function(caller) {
        var char_name = $("#char_name").val();
        commands.createCharacter(char_name);
        $("#char_name").val("");
    },
};

$(document).ready(function() {
	controller.onReady();
});