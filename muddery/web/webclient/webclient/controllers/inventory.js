
var controller = {

    // Set player's inventory
    setInventory: function(inventory) {
        this.clearItems();
        
        var container = $("#inventory_items");
        var item_template = container.find("tr.template");
        for (var i in inventory) {
            var obj = inventory[i];
            var item = item_template.clone()
	            .removeClass("template");

            item.find(".obj_name")
                .data("dbref", obj["dbref"])
            	.text(obj["name"]);
            
            if (obj["icon"]) {
            	item.find(".img_icon").attr("src", settings.resource_location + obj["icon"]);
            	item.find(".obj_icon").show();
            }
            else {
            	item.find(".obj_icon").hide();
            }
            
            var number = obj["number"];
            if ("equipped" in obj && obj["equipped"]) {
                number += _(" (equipped)");
            }
            item.find(".obj_number").text(number);

			var desc = text2html.parseHtml(obj["desc"]);
            item.find(".obj_desc").html(desc);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#inventory_items>:not(.template)").remove();
    },
    
    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        parent.commands.doLook(dbref);
    },
};
