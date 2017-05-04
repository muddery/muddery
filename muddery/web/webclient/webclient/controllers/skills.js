
var controller = {

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
            	var icon = settings.resource_location + obj["icon"];
            	item.find(".img_icon").attr("src", icon);
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
        parent.commands.doLook(dbref);
    },
};
