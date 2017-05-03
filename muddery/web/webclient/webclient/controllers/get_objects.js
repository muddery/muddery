
var controller = {

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },

	setGetObjects: function(accepted, rejected) {
		// set new objects
		this.setItems("#accepted", "#accepted_list", accepted);
		this.setItems("#rejected", "#rejected_list", rejected);
	},

    setItems: function(block_id, content_id, objects) {
    	var content = $(content_id);
    	
    	// Remove items that are not template.
    	content.children().not(".template").remove();
    	
    	// Add new items.
		var item_template = content.find("p.template");

		var has_item = false;
		if (objects) {
            for (var name in objects) {
				var item = item_template.clone()
					.removeClass("template")
				item.find(".name").text(name);
				item.find(".info").text(objects[name]);
				item.appendTo(content);
				
				has_item = true;
            }
		}
		
		if (has_item) {
            $(block_id).show();
        }
		else {
			$(block_id).hide();
		}
    },
};
