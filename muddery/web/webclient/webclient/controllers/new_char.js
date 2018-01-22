//@ sourceURL=/controller/new_char.js

/*
 * Derive from the base class.
 */
function MudderyNewChar(root_controller) {
	BaseController.call(this, root_controller);
}

MudderyNewChar.prototype = prototype(BaseController.prototype);
MudderyNewChar.prototype.constructor = MudderyNewChar;

/*
 * Reset the view's language.
 */
MudderyNewChar.prototype.resetLanguage = function() {
	$("#view_header").text($$("Set Character"));
	$("#view_name").text($$("Name"));
	$("#button_create").text($$("Create"));
	$("#char_name").attr("placeholder", $$("name"));
}

/*
 * Bind events.
 */
MudderyNewChar.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
    this.onClick("#button_create", this.onCreate);
}

/*
 * Event when clicks the close button.
 */
MudderyNewChar.prototype.onClose = function(element) {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks the create button.
 */
MudderyNewChar.prototype.onCreate = function(element) {
	var char_name = $("#char_name").val();
	$$.commands.createCharacter(char_name);
	$("#char_name").val("");
}
