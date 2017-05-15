
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
	},
	
    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

	setMessage: function(header, content, commands) {
	    header = text2html.parseHtml(header);
	    $("#popup_header").html(header);

	    content = text2html.parseHtml(content);
		$("#popup_body").html(content);

        this.clearButtons();
		if (!commands) {
            commands = [{"name": _("OK"),
                         "cmd": "",
                         "args": ""}];
        }
		this.addButtons(commands);
	},

	clearButtons: function() {
    	// remove buttons that are not template..
    	$("#popup_footer>:not(.template)").remove();
    },

	addButtons: function(buttons) {
    	var container = $("#popup_footer");
		var item_template = container.find("button.template");

		if (buttons) {
            for (var i in buttons) {
                var button = buttons[i];

                var name = text2html.parseHtml(button["name"]);
                item_template.clone()
                    .removeClass("template")
                    .data("cmd_name", button["cmd"])
                    .data("cmd_args", button["args"])
                    .html(name)
                    .appendTo(container);
            }
        }
    },

    doCommandLink: function(caller) {
        this.doClosePopupBox();

        var cmd = $(caller).data("cmd_name");
        var args = $(caller).data("cmd_args");
        if (cmd) {
            commands.doCommandLink(cmd, args);
        }
    },
};

$(document).ready(function() {
	controller.onReady();
});