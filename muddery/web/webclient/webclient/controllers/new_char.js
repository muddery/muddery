//@ sourceURL=/controller/new_char.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#view_header").text($$("Set Character"));
	$("#view_name").text($$("Name"));
	$("#button_create").text($$("Create"));
	$("#char_name").attr("placeholder", $$("name"));
}

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
Controller.prototype.onClose = function(event) {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks the create button.
 */
Controller.prototype.onCreate = function(event) {
	var char_name = $("#char_name").val();
	$$.commands.createCharacter(char_name);
	$("#char_name").val("");
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});