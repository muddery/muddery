
var _ = parent._;
var parent_controller = parent.controller;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#popup_header").text(_("Get Objects"));
		$("#view_get_objects").text(_("Get Objects: "));
		$("#view_rejected").text(_("Can Not Get: "));
		$("#view_button_ok").text(_("OK"));
	},
	
    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

	setGetObjects: function(accepted, rejected) {
		// set new objects
		this.setItems("#accepted", "#accepted_list", accepted);
		this.setItems("#rejected", "#rejected_list", rejected);
	},

    setItems: function(block_id, container_id, objects) {
    	var container = $(container_id);
    	
    	// Remove items that are not template.
    	container.children().not(".template").remove();
    	
    	// Add new items.
		var item_template = container.find("p.template");

		var has_item = false;
		if (objects) {
            for (var name in objects) {
				var item = item_template.clone()
					.removeClass("template")
				item.find(".name").text(name);
				item.find(".info").text(objects[name]);
				item.appendTo(container);
				
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

$(document).ready(function() {
	controller.onReady();
});