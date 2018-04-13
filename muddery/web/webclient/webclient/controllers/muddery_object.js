
if (typeof(require) != "undefined") {
    require("./base_controller.js");
}

/*
 * Derive from the base class.
 */
function MudderyObject(el) {
	BasePopupController.call(this, el);
	
	this.dbref = null;
}

MudderyObject.prototype = prototype(BasePopupController.prototype);
MudderyObject.prototype.constructor = MudderyObject;

/*
 * Bind events.
 */
MudderyObject.prototype.bindEvents = function() {
    this.onClick("#object_close_box", this.onClose);
	this.onClick("#object_popup_footer", "button", this.onCommand);
}

/*
 * Event when clicks the close button.
 */
MudderyObject.prototype.onClose = function(element) {
	$$.main.doClosePopupBox();
}

/*
 * Event when clicks a command button.
 */
MudderyObject.prototype.onCommand = function(element) {
	this.onClose();

	var cmd = this.select(element).data("cmd_name");
	var args = this.select(element).data("cmd_args");
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
	this.select("#object_popup_header").html($$.text2html.parseHtml(name));

	// add icon
	if (icon) {
		var url = settings.resource_url + icon;
		this.select("#object_img_icon").attr("src", url);
		this.select("#object_div_icon").show();
    }
    else {
        this.select("#object_div_icon").hide();
    }

	// add desc
	desc = $$.text2html.parseHtml(desc);
	this.select("#object_popup_body").html(desc);
		    
    this.clearElements("#object_popup_footer");
	if (!commands) {
        commands = [{"name": $$.trans("OK"),
                     "cmd": "",
                     "args": ""}];
    }
	this.addButtons(commands);
}

/*
 * Set command buttons.
 */
MudderyObject.prototype.addButtons = function(commands) {
	var template = this.select("#object_popup_footer>button.template");

	for (var i in commands) {
		var button = commands[i];
		var item = this.cloneTemplate(template);

		var name = $$.text2html.parseHtml(button["name"]);
		item.data("cmd_name", button["cmd"])
			.data("cmd_args", button["args"])
			.html(name);
	}
}
