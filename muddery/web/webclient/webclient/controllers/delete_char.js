//@ sourceURL=/controller/delete_char.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
	this.name = "";
    this.dbref = "";
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#view_header").text($$("Delete") + " " + this.name);
	$("#view_password").text($$("Verify Password"));
	$("#button_delete").text($$("Delete"));
	$("#password").attr("placeholder", $$("password"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
	$("#button_delete").bind("click", this.onDelete);
}

/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function(event) {
    $$.controller.doClosePopupBox();
}

/*
 * Event when clicks the delete button.
 */
Controller.prototype.onDelete = function(event) {
	var password = $("#password").val();
	$$.commands.deleteCharacter(controller.dbref, password);

	$("#password").val("");
}

/*
 * Set character's data.
 */
Controller.prototype.setData = function(name, dbref) {
	this.name = name;
	this.dbref = dbref;

	$("#view_header").text($$("Delete") + " " + this.name);
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
