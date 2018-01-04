
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();

        $("#button_queue").bind("click", this.onQueueUpCombat);
        $("#button_quit").bind("click", this.onQuitCombatQueue);
    },

	// reset view's language
	resetLanguage: function() {
	    $("#button_fight").text(_("FIGHT"));
		$("#view_ranking").text(_("RANKING"));
		$("#view_name").text(_("NAME"));
		$("#view_honour").text(_("HONOUR"));
		$("#button_queue").text(_("QUEUE UP"));
		$("#button_quit").text(_("QUIT QUEUE"));
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
    
    onQueueUpCombat: function() {
        controller.queueUpCombat();
        commands.queueUpCombat();
    },

    queueUpCombat: function() {
        $("#button_queue").hide();
	    $("#button_quit").show();
    },

    onQuitCombatQueue: function() {
	    controller.quitCombatQueue();
        commands.quitCombatQueue();
    },

    quitCombatQueue: function() {
	    $("#button_queue").show();
	    $("#button_quit").hide();
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
