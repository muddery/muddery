
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
    _name: "",
    _dbref: "",

	// on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_header").text(_("Delete") + " " + this._name);
		$("#view_password").text(_("Verify Password"));
		$("#button_delete").text(_("Delete"));
		$("#password").attr("placeholder", _("password"));
	},

	// set character's data
	setData: function(name, dbref) {
	    this._name = name;
	    this._dbref = dbref;

	    $("#view_header").text(_("Delete") + " " + this._name);
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

    deleteCharacter: function(caller) {
        var password = $("#password").val();
        commands.deleteCharacter(this._dbref, password);

        $("#password").val("");
    },
};

$(document).ready(function() {
	controller.onReady();
});