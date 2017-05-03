
var controller = {

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },

	setObject: function(name, icon, desc, commands) {
		// add name
	    try {
	        name = text2html.parseHtml(name);
	    }
	    catch(error) {
            console.error(error.message);
        }
	    $("#popup_header").html(name);
	    	
		// add icon
		if (icon) {
			var url = settings.resource_location + icon;
			$("#img_icon").attr("src", url);
        }
        else {
            $("#img_icon").hide();
        }

		// add desc
        try {
	        desc = text2html.parseHtml(desc);
	    }
	    catch(error) {
            console.error(error.message);
        }
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
    	$("#button_content>:not(.template)").remove();
    },

	addButtons: function(data) {
    	var content = $("#button_content");
		var item_template = content.find("button.template");

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                try {
                    var name = text2html.parseHtml(cmd["name"]);
                    item_template.clone()
                        .removeClass("template")
                        .data("cmd_name", cmd["cmd"])
                        .data("cmd_args", cmd["args"])
                        .html(name)
                        .appendTo(content);

                    has_button = true;
                }
                catch(error) {
                    console.error(error.message);
                }
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
