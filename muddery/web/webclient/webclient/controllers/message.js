//@ sourceURL=/controller/message.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
	$("#button_create").bind("click", this.onCreate);
}
	
/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function() {
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
 * Set message's data.
 */
Controller.prototype.setMessage = function(header, content, commands) {
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