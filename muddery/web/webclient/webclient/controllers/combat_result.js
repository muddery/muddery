
var _ = parent._;
var parent_controller = parent.controller;

var controller = {
	_dialogue: null,

	// on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_get_exp").text(_("Get Exp: "));
		$("#view_get_objects").text(_("Get Objects: "));
		$("#view_rejected").text(_("Can Not Get: "));
		$("#view_button_ok").text(_("OK"));
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
        
        // show dialogue after combat
        if (this._dialogue) {
            parent_controller.setDialogueList(this._dialogue);
        }
    },
    
    clear: function() {
    	$("#header").empty();
    	$("#desc").empty();
    	$("#exp").text(0);
    	$("#accepted").hide();
    	$("#rejected").hide();
            
        this._dialogue = null;
    },

	setResult: function(result) {
	    // result
	    if (!result) {
	    	return;
	    }
	    
	    var header = "";
        if ("escaped" in result) {
           header = _("Escaped !");
        }
        else if ("win" in result) {
            header = _("You win !");
        }
        else if ("lose" in result) {
            header = _("You lost !");
        }
        
        $("#header").text(header);
	},
	
	setGetExp: function(exp) {
		$("#exp").text(exp);
	},
	
	setDialogue: function(dialogue) {
		this._dialogue = dialogue;
	},
	
	setGetObjects: function(accepted, rejected) {
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