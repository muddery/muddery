
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
		$("#view_name").text(_("NAME"));
		$("#view_desc").text(_("DESC"));
	},
	
    // Set player's inventory
    setSkills: function(skills) {
        this.clearItems();
        
        var container = $("#skill_list");
        var item_template = container.find("tr.template");
        for (var i in skills) {
            var obj = skills[i];
            var item = item_template.clone()
	            .removeClass("template");

            item.find(".skill_name")
                .data("dbref", obj["dbref"])
            	.text(obj["name"]);
            
            if (obj["icon"]) {
            	item.find(".img_icon").attr("src", settings.resource_url + obj["icon"]);
            	item.find(".skill_icon").show();
            }
            else {
            	item.find(".skill_icon").hide();
            }

			var desc = text2html.parseHtml(obj["desc"]);
            item.find(".skill_desc").html(desc);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#skill_list>:not(.template)").remove();
    },
    
    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.doLook(dbref);
    },
};

$(document).ready(function() {
	controller.onReady();
});
