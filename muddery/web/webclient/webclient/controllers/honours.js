
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_ranking").text(_("RANKING"));
		$("#view_name").text(_("NAME"));
		$("#view_honour").text(_("HONOUR"));
	},
	
    // Set top characters
    setRankings: function(rankings) {
        this.clearItems();
        
        var container = $("#character_items");
        var item_template = container.find("tr.template");
        for (var i in rankings) {
            var data = rankings[i];
            var item = item_template.clone()
	            .removeClass("template");

            item.find(".character_ranking")
            	.text(data["ranking"]);

            item.find(".character_name")
            	.text(data["name"]);

			item.find(".character_honour")
            	.text(data["honour"]);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#character_items>:not(.template)").remove();
    },
    
    makeMatch: function() {
        commands.makeMatch();
    },
};

$(document).ready(function() {
	controller.onReady();
});
