
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
	$("#del_char_view_header").text($$("Delete") + " " + this.name);
	$("#del_char_view_password").text($$("Verify Password"));
	$("#del_char_button_delete").text($$("Delete"));
	$("#del_char_password").attr("placeholder", $$("password"));
}

/*
 * Bind events.
 */
MudderyDeleteChar.prototype.bindEvents = function() {
    this.onClick("#del_char_close_box", this.onClose);
	this.onClick("#del_char_button_delete", this.onDelete);
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
	var password = $("#del_char_password").val();
	$$.commands.deleteCharacter(this.dbref, password);

	$("#del_char_password").val("");
}

/*
 * Set character's data.
 */
MudderyDeleteChar.prototype.setData = function(name, dbref) {
	this.name = name;
	this.dbref = dbref;

	$("#del_char_view_header").text($$("Delete") + " " + this.name);
}
