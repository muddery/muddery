//@ sourceURL=/controller/muddery_object.js

/*
 * Derive from the base class.
 */
function MudderyObject() {
	BaseController.call(this);
	
	this.dbref = null;
}

MudderyObject.prototype = prototype(BaseController.prototype);
MudderyObject.prototype.constructor = MudderyObject;

/*
 * Bind events.
 */
MudderyObject.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
	this.onClick("#popup_footer", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyObject.prototype.onClose = function(element) {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks a command button.
 */
MudderyObject.prototype.onCommand = function(element) {
	this.onClose();

	var cmd = $(element).data("cmd_name");
	var args = $(element).data("cmd_args");
	if (cmd) {
		$$.commands.doCommandLink(cmd, args);
	}
}

/*
 * Event when an object moved out from the current place.
 */
MudderyObject.prototype.onObjMovedOut = function(dbref) {
	if (dbref == this.dbref) {
		this.onClose();
	}
}

/*
 * Event when objects moved out from the current place.
 */
MudderyObject.prototype.onObjsMovedOut = function(objects) {
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
MudderyObject.prototype.setObject = function(dbref, name, icon, desc, commands) {
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
MudderyObject.prototype.addButtons = function(commands) {
	var template = $("#popup_footer>button.template");

	for (var i in commands) {
		var button = commands[i];
		var item = this.cloneTemplate(template);

		var name = $$.text2html.parseHtml(button["name"]);
		item.data("cmd_name", button["cmd"])
			.data("cmd_args", button["args"])
			.html(name);
	}
}
