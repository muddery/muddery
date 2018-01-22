//@ sourceURL=/controller/message.js

/*
 * Derive from the base class.
 */
function MudderyMessage(root_controller) {
	BaseController.call(this, root_controller);
}

MudderyMessage.prototype = prototype(BaseController.prototype);
MudderyMessage.prototype.constructor = MudderyMessage;

/*
 * Bind events.
 */
MudderyMessage.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
	this.onClick("#popup_footer", "button", this.onCommand);
}
	
/*
 * Event when clicks the close button.
 */
MudderyMessage.prototype.onClose = function(element) {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks a command button.
 */
MudderyMessage.prototype.onCommand = function(element) {
	this.onClose();

	var cmd = $(element).data("cmd_name");
	var args = $(element).data("cmd_args");
	if (cmd) {
		$$.commands.doCommandLink(cmd, args);
	}
}

/*
 * Set message's data.
 */
MudderyMessage.prototype.setMessage = function(header, content, commands) {
	$("#popup_header").html($$.text2html.parseHtml(header));

	$("#popup_body").html($$.text2html.parseHtml(content));

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
MudderyMessage.prototype.addButtons = function(commands) {
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
