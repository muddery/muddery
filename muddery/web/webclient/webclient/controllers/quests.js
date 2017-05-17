
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var commands = parent.commands;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_name").text(_("NAME"));
		$("#view_desc").text(_("DESC"));
		$("#view_objective").text(_("OBJECTIVE"));
	},
	
    // Set player's quests
    setQuests: function(quests) {
        this.clearItems();
        
        var container = $("#quest_list");
        var item_template = container.find("tr.template");
        for (var i in quests) {
            var quest = quests[i];
            var item = item_template.clone()
	            .removeClass("template");

            item.find(".quest_name")
                .data("dbref", quest["dbref"])
            	.text(quest["name"]);
            
			var desc = text2html.parseHtml(quest["desc"]);
            item.find(".quest_desc").html(desc);
            
            var obj_container = item.find(".quest_objective");
            var obj_template = obj_container.find("p.template");
            for (var o in quest["objectives"]) {
				var objective = quest["objectives"][o];
				var obj_item = obj_template.clone()
					.removeClass("template");

				if ("desc" in objective) {
					obj_item.text(objective["desc"]);
				}
				else {
					obj_item.text(objective.target + " " +
								  objective.object + " " +
								  objective.accomplished + "/" +
								  objective.total);
				}
				
				obj_item.appendTo(obj_container);
			}
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#quest_list>:not(.template)").remove();
    },
    
    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.doLook(dbref);
    },
};

$(document).ready(function() {
	controller.onReady();
});
