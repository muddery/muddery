
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
	
	_dbref: null,

    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
	},
	
	getObject: function() {
		return this._dbref;
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

	setObject: function(dbref, name, icon, desc, commands) {
		this._dbref = dbref;
		
		// add name
	    name = text2html.parseHtml(name);
	    $("#popup_header").html(name);

		// add icon
		if (icon) {
			var url = settings.resource_url + icon;
			$("#img_icon").attr("src", url);
			$("#div_icon").show();
        }
        else {
            $("#div_icon").hide();
        }

		// add desc
	    desc = text2html.parseHtml(desc);
		$("#popup_body").html(desc);
		    
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
