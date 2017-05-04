
var controller = {

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
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
    	$("#button_content>:not(.template)").remove();
    },

	addButtons: function(data) {
    	var content = $("#button_content");
		var item_template = content.find("button.template");

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                var name = text2html.parseHtml(cmd["name"]);
                item_template.clone()
                    .removeClass("template")
                    .data("cmd_name", cmd["cmd"])
                    .data("cmd_args", cmd["args"])
                    .html(name)
                    .appendTo(content);

                has_button = true;
            }
        }
    },

    doCommandLink: function(caller) {
        this.doClosePopupBox();

        var cmd = $(caller).data("cmd_name");
        var args = $(caller).data("cmd_args");
        if (cmd) {
            parent.commands.doCommandLink(cmd, args);
        }
    },
};
