//@ sourceURL=/controller/object.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
	this.dbref = null;
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
}

/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function(event) {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks a command button.
 */
Controller.prototype.onCommand = function(event) {
	controller.onClose();

	var cmd = $(this).data("cmd_name");
	var args = $(this).data("cmd_args");
	if (cmd) {
		$$.commands.doCommandLink(cmd, args);
	}
}

/*
 * Event when an object moved out from the current place.
 */
Controller.prototype.onObjMovedOut = function(dbref) {
	if (dbref == this.dbref) {
		this.onClose();
	}
}

/*
 * Event when objects moved out from the current place.
 */
Controller.prototype.onObjsMovedOut = function(objects) {
    for (var key in objects) {
        for (var i in objects[key]) {
            if (objects[key][i]["dbref"] == this.dbref) {
                this.onClose();
                return;
            }
        }
    }
}

/*
 * Set object's data.
 */
Controller.prototype.setObject = function(dbref, name, icon, desc, commands) {
	this.dbref = dbref;
		
	// add name
	$("#popup_header").html($$.text2html.parseHtml(name));

	// add icon
	if (icon) {
		var url = $$.settings.resource_url + icon;
		$("#img_icon").attr("src", url);
		$("#div_icon").show();
    }
    else {
        $("#div_icon").hide();
    }

	// add desc
	desc = $$.text2html.parseHtml(desc);
	$("#popup_body").html(desc);
		    
    this.clearElements("#popup_footer");
	if (!commands) {
        commands = [{"name": $$("OK"),
                     "cmd": "",
                     "args": ""}];
    }
	this.addButtons(commands);
}

/*
 * Set command buttons.
 */
Controller.prototype.addButtons = function(commands) {
	var template = $("#popup_footer>button.template");

	for (var i in commands) {
		var button = commands[i];
		var item = this.cloneTemplate(template);

		var name = $$.text2html.parseHtml(button["name"]);
		item.data("cmd_name", button["cmd"])
			.data("cmd_args", button["args"])
			.html(name)
			.bind("click", this.onCommand);
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
