//@ sourceURL=/controller/muddery_select_char.js

/*
 * Derive from the base class.
 */
function MudderySelectChar() {
	BaseController.call(this);
}

MudderySelectChar.prototype = prototype(BaseController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Reset the view's language.
 */
MudderySelectChar.prototype.resetLanguage = function() {
    $("#view_character").text($$("Characters"));
	$("#button_new_char").text($$("New Character"));
}

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick("#button_new_char", this.onNewCharacter);
    this.onClick("#character_items", ".char_name", this.onSelectCharacter);
    this.onClick("#character_items", ".button_delete", this.onDeleteCharacter);
}

/*
 * Event when clicks the new character button.
 */
MudderySelectChar.prototype.onNewCharacter = function(element) {
    $$.controller.showNewCharacter();
}

/*
 * On select a character.
 */
MudderySelectChar.prototype.onSelectCharacter = function(element) {
    var dbref = $(element).data("dbref");
    $$.commands.puppetCharacter(dbref);
}
    
/*
 * On delete a character.
 */
MudderySelectChar.prototype.onDeleteCharacter = function(element) {
	var name = $(element).data("name");
	var dbref = $(element).data("dbref");
	$$.controller.showDeleteCharacter(name, dbref);
}
    
/*
 * Set playable characters.
 */
MudderySelectChar.prototype.setCharacters = function(characters) {
    this.clearElements("#character_items");
	var template = $("#character_items>.template");

	for (var i in characters) {
		var obj = characters[i];
		var item = this.cloneTemplate(template);

		item.find(".char_name")
			.data("dbref", obj["dbref"])
			.text(obj["name"]);

		item.find(".button_delete")
			.data("name", obj["name"])
			.data("dbref", obj["dbref"]);
	}
}
