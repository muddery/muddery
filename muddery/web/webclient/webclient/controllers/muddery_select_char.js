
if (typeof(require) != "undefined") {
    require("../css/select_char.css");

    require("../controllers/base_controller.js");
}

/*
 * Derive from the base class.
 */
MudderySelectChar = function(el) {
	BaseController.call(this, el);
}

MudderySelectChar.prototype = prototype(BaseController.prototype);
MudderySelectChar.prototype.constructor = MudderySelectChar;

/*
 * Reset the view's language.
 */
MudderySelectChar.prototype.resetLanguage = function() {
    this.select("#char_view_character").text($$.trans("Characters"));
	this.select("#char_button_new_char").text($$.trans("New Character"));
}

/*
 * Bind events.
 */
MudderySelectChar.prototype.bindEvents = function() {
    this.onClick("#char_button_new_char", this.onNewCharacter);
    this.onClick("#character_items", ".char_name", this.onSelectCharacter);
    this.onClick("#character_items", ".button_delete", this.onDeleteCharacter);
}

/*
 * Event when clicks the new character button.
 */
MudderySelectChar.prototype.onNewCharacter = function(element) {
    $$.main.showNewCharacter();
}

/*
 * On select a character.
 */
MudderySelectChar.prototype.onSelectCharacter = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.puppetCharacter(dbref);
}
    
/*
 * On delete a character.
 */
MudderySelectChar.prototype.onDeleteCharacter = function(element) {
	var name = this.select(element).data("name");
	var dbref = this.select(element).data("dbref");
	$$.main.showDeleteCharacter(name, dbref);
}
    
/*
 * Set playable characters.
 */
MudderySelectChar.prototype.setCharacters = function(characters) {
    this.clearElements("#character_items");
	var template = this.select("#character_items>.template");

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
