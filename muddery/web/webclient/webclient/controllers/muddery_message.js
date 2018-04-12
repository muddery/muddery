
/*
 * Derive from the base class.
 */
function MudderyMessage(el) {
	BasePopupController.call(this, el);
}

MudderyMessage.prototype = prototype(BasePopupController.prototype);
MudderyMessage.prototype.constructor = MudderyMessage;

/*
 * Bind events.
 */
MudderyMessage.prototype.bindEvents = function() {
    this.onClick("#msg_close_box", this.onClose);
	this.onClick("#msg_popup_footer", "button", this.onCommand);
}
	
/*
 * Event when clicks the close button.
 */
MudderyMessage.prototype.onClose = function(element) {
	$$.main.doClosePopupBox();
}

/*
 * Event when clicks a command button.
 */
MudderyMessage.prototype.onCommand = function(element) {
	this.onClose();

	var cmd = this.select(element).data("cmd_name");
	var args = this.select(element).data("cmd_args");
	if (cmd) {
		$$.commands.doCommandLink(cmd, args);
	}
}

/*
 * Set message's data.
 */
MudderyMessage.prototype.setMessage = function(header, content, commands) {
	this.select("#msg_popup_header").html($$.text2html.parseHtml(header));

	this.select("#msg_popup_body").html($$.text2html.parseHtml(content));

	this.clearElements("#msg_popup_footer");
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
MudderyMessage.prototype.addButtons = function(commands) {
	var template = this.select("#msg_popup_footer>button.template");

	for (var i in commands) {
		var button = commands[i];
		var item = this.cloneTemplate(template);

		var name = $$.text2html.parseHtml(button["name"]);
		item.data("cmd_name", button["cmd"])
			.data("cmd_args", button["args"])
			.html(name);
	}
}
