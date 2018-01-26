//@ sourceURL=/controller/muddery_delete_char.js

/*
 * Derive from the base class.
 */
function MudderyDeleteChar() {
	BaseController.call(this);
	
	this.name = "";
    this.dbref = "";
}

MudderyDeleteChar.prototype = prototype(BaseController.prototype);
MudderyDeleteChar.prototype.constructor = MudderyDeleteChar;

/*
 * Reset the view's language.
 */
MudderyDeleteChar.prototype.resetLanguage = function() {
	$("#view_header").text($$("Delete") + " " + this.name);
	$("#view_password").text($$("Verify Password"));
	$("#button_delete").text($$("Delete"));
	$("#password").attr("placeholder", $$("password"));
}

/*
 * Bind events.
 */
MudderyDeleteChar.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
	this.onClick("#button_delete", this.onDelete);
}

/*
 * Event when clicks the close button.
 */
MudderyDeleteChar.prototype.onClose = function(element) {
    $$.controller.doClosePopupBox();
}

/*
 * Event when clicks the delete button.
 */
MudderyDeleteChar.prototype.onDelete = function(element) {
	var password = $("#password").val();
	$$.commands.deleteCharacter(this.dbref, password);

	$("#password").val("");
}

/*
 * Set character's data.
 */
MudderyDeleteChar.prototype.setData = function(name, dbref) {
	this.name = name;
	this.dbref = dbref;

	$("#view_header").text($$("Delete") + " " + this.name);
}
