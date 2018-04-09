
/*
 * Derive from the base class.
 */
function MudderyNewChar(el) {
	BaseController.call(this, el);
}

MudderyNewChar.prototype = prototype(BaseController.prototype);
MudderyNewChar.prototype.constructor = MudderyNewChar;

/*
 * Reset the view's language.
 */
MudderyNewChar.prototype.resetLanguage = function() {
	this.select("#new_char_view_header").text($$("Set Character"));
	this.select("#new_char_view_name").text($$("Name"));
	this.select("#new_char_button_create").text($$("Create"));
	this.select("#new_char_name").attr("placeholder", $$("name"));
}

/*
 * Bind events.
 */
MudderyNewChar.prototype.bindEvents = function() {
    this.onClick("#new_char_close_box", this.onClose);
    this.onClick("#new_char_button_create", this.onCreate);
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
	var char_name = this.select("#new_char_name").val();
	$$.commands.createCharacter(char_name);
	this.select("#new_char_name").val("");
}
