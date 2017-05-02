
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
            
            var name = obj["name"];
            item.find(".obj_name")
                .data("dbref", obj["dbref"])
            	.text(name);
            
            if (obj["icon"]) {
            	var icon = settings.resource_location + obj["icon"];
            	item.find(".img_icon").attr("src", icon);
            }
            else {
            	item.find(".obj_icon").hide();
            }
            
            var number = obj["number"];
            if ("equipped" in obj && obj["equipped"]) {
                number += _(" (equipped)");
            }
            item.find(".obj_number").text(number);

			var desc = "";
            try {
            	desc = text2html.parseHtml(obj["desc"]);
            }
			catch(error) {
                console.error(error.message);
    	    }
            item.find(".obj_desc").html(desc);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#tab_inventory tbody").children().not(".template").remove();
    },
    
    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        parent.commands.doLook(dbref);
    },
};
