
/*
 * Derive from the base class.
 */
function MudderyCombatResult() {
	BaseController.call(this);
	
    this.dialogue = null;
}

MudderyCombatResult.prototype = prototype(BaseController.prototype);
MudderyCombatResult.prototype.constructor = MudderyCombatResult;

/*
 * Reset the view's language.
 */
MudderyCombatResult.prototype.resetLanguage = function() {
	$("#combat_result_view_get_exp").text($$("Get Exp: "));
	$("#combat_result_view_get_objects").text($$("Get Objects: "));
	$("#combat_result_view_rejected").text($$("Can Not Get: "));
	$("#combat_result_button_ok").text($$("OK"));
}

/*
 * Bind events.
 */
MudderyCombatResult.prototype.bindEvents = function() {
    this.onClick("#combat_result_button_ok", this.onClose);
}

/*
 * Event when clicks the close button.
 */
MudderyCombatResult.prototype.onClose = function(element) {
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
MudderyCombatResult.prototype.clear = function() {
	$("#combat_result_header").empty();
	$("#combat_result_desc").empty();
	$("#combat_result_exp").text(0);
	$("#combat_result_accepted").hide();
	$("#combat_result_rejected").hide();
		
	this.dialogue = null;
}

/*
 * Set result data.
 */
MudderyCombatResult.prototype.setResult = function(result) {
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
	
	$("#combat_result_header").text(header);
}
	
/*
 * Set the experiences that the player get.
 */
MudderyCombatResult.prototype.setGetExp = function(exp) {
	$("#combat_result_exp").text(exp);
}
	
/*
 * Set dialogues after the combat.
 */
MudderyCombatResult.prototype.setDialogue = function(dialogue) {
	this.dialogue = dialogue;
}
	
/*
 * Set the objects that the player get.
 */
MudderyCombatResult.prototype.setGetObjects = function(accepted, rejected) {
	this.setItems("#combat_result_accepted", "#combat_result_accepted_list", accepted);
	this.setItems("#combat_result_rejected", "#combat_result_rejected_list", rejected);
}
	
/*
 * Set object items.
 */
MudderyCombatResult.prototype.setItems = function(block_id, container_id, objects) {
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
