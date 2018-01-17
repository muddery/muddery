//@ sourceURL=/controller/select_char.js

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
    $("#view_character").text($$("Characters"));
	$("#button_new_char").text($$("New Character"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#button_new_char").bind("click", this.onNewCharacter);
}

/*
 * Event when clicks the new character button.
 */
Controller.prototype.onNewCharacter = function(event) {
    $$.controller.showNewCharacter();
}

/*
 * On select a character.
 */
Controller.prototype.onSelectCharacter = function(event) {
    var dbref = $(this).data("dbref");
    $$.commands.puppetCharacter(dbref);
}
    
/*
 * On delete a character.
 */
Controller.prototype.onDeleteCharacter = function(event) {
	var name = $(this).data("name");
	var dbref = $(this).data("dbref");
	$$.controller.showDeleteCharacter(name, dbref);
}
    
/*
 * Set playable characters.
 */
Controller.prototype.setCharacters = function(characters) {
    this.clearElements("#character_items");
	var template = $("#character_items>.template");

	for (var i in characters) {
		var obj = characters[i];
		var item = this.cloneTemplate(template);

		item.find(".char_name")
			.data("dbref", obj["dbref"])
			.text(obj["name"])
			.bind("click", this.onSelectCharacter);

		item.find(".button_delete")
			.data("name", obj["name"])
			.data("dbref", obj["dbref"])
			.bind("click", this.onDeleteCharacter);
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
