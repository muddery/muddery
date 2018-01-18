//@ sourceURL=/controller/combat_result.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
    this.dialogue = null;
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#view_get_exp").text($$("Get Exp: "));
	$("#view_get_objects").text($$("Get Objects: "));
	$("#view_rejected").text($$("Can Not Get: "));
	$("#button_ok").text($$("OK"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#button_ok").bind("click", this.onClose);
}

/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function(event) {
	// close popup box
    $$.controller.doClosePopupBox();

	// show dialogue after combat
	if (this.dialogue) {
		$$.controller.setDialogueList(this.dialogue);
	}
}
    
/*
 * Clear the result box.
 */
Controller.prototype.clear = function() {
	$("#header").empty();
	$("#desc").empty();
	$("#exp").text(0);
	$("#accepted").hide();
	$("#rejected").hide();
		
	this.dialogue = null;
}

/*
 * Set result data.
 */
Controller.prototype.setResult = function(result) {
	// result
	if (!result) {
		return;
	}
	
	var header = "";
	if ("escaped" in result) {
	   header = $$("Escaped !");
	}
	else if ("win" in result) {
		header = $$("You win !");
	}
	else if ("lose" in result) {
		header = $$("You lost !");
	}
	else if ("draw" in result) {
		header = $$("Draw !");
	}
	
	$("#header").text(header);
}
	
/*
 * Set the experiences that the player get.
 */
Controller.prototype.setGetExp = function(exp) {
	$("#exp").text(exp);
}
	
/*
 * Set dialogues after the combat.
 */
Controller.prototype.setDialogue = function(dialogue) {
	this.dialogue = dialogue;
}
	
/*
 * Set the objects that the player get.
 */
Controller.prototype.setGetObjects = function(accepted, rejected) {
	this.setItems("#accepted", "#accepted_list", accepted);
	this.setItems("#rejected", "#rejected_list", rejected);
}
	
/*
 * Set object items.
 */
Controller.prototype.setItems = function(block_id, container_id, objects) {
	this.clearElements(container_id);
	var template = $(container_id).find("p.template");

	var has_item = false;
	if (objects) {
		for (var name in objects) {
			var item = this.cloneTemplate(template);
			item.find(".name").text(name);
			item.find(".info").text(objects[name]);
			
			has_item = true;
		}
	}
	
	if (has_item) {
		$(block_id).show();
	}
	else {
		$(block_id).hide();
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});