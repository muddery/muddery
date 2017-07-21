
var _ = parent._;
var parent_controller = parent.controller;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_character").text(_("Characters"));
		$("#view_new_char").text(_("New Character"));
	},
	
    // Set playable characters.
    setCharacters: function(characters) {
        this.clearItems();
        
        var container = $("#character_items");
        var item_template = container.find("div.template");
        for (var i in characters) {
            var obj = characters[i];
            var item = item_template.clone()
	            .removeClass("template");

            item.find(".char_name")
                .data("dbref", obj["dbref"])
            	.text(obj["name"]);

            item.find(".button_delete")
                .data("name", obj["name"])
                .data("dbref", obj["dbref"]);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#character_items>:not(.template)").remove();
    },
    
    selectCharacter: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.puppetCharacter(dbref);
    },
    
    newCharacter: function(caller) {
        parent_controller.showNewCharacter();
    },

    deleteCharacter: function(caller) {
        var name = $(caller).data("name");
        var dbref = $(caller).data("dbref");
        parent_controller.showDeleteCharacter(name, dbref);
    },
};

$(document).ready(function() {
	controller.onReady();
});
