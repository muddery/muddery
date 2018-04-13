
if (typeof(require) != "undefined") {
    require("../controllers/base_controller.js");
}

/*
 * Derive from the base class.
 */
MudderyGetObjects = function(el) {
	BasePopupController.call(this, el);
	
	this.goods = [];
}

MudderyGetObjects.prototype = prototype(BasePopupController.prototype);
MudderyGetObjects.prototype.constructor = MudderyGetObjects;

/*
 * Reset the view's language.
 */
MudderyGetObjects.prototype.resetLanguage = function() {
	this.select("#get_obj_popup_header").text($$.trans("Get Objects"));
	this.select("#get_obj_view_get_objects").text($$.trans("Get Objects: "));
	this.select("#get_obj_view_rejected").text($$.trans("Can Not Get: "));
	this.select("#get_obj_view_button_ok").text($$.trans("OK"));
}

/*
 * Bind events.
 */
MudderyGetObjects.prototype.bindEvents = function() {
    this.onClick("#get_obj_close_box", this.onClose);
    this.onClick("#get_obj_button_ok", this.onClose);
}

/*
 * Event when clicks the close button.
 */
MudderyGetObjects.prototype.onClose = function(element) {
    $$.main.doClosePopupBox();
}

/*
 * Set objects that the user get.
 */
MudderyGetObjects.prototype.setObjects = function(accepted, rejected) {
	// set new objects
	this.setItems("#get_obj_accepted", "#get_obj_accepted_list", accepted);
	this.setItems("#get_obj_rejected", "#get_obj_rejected_list", rejected);
}

/*
 * Set object items.
 */
MudderyGetObjects.prototype.setItems = function(block_id, container_id, objects) {
	this.clearElements(container_id);
	var template = this.select(container_id).find("p.template");

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
		this.select(block_id).show();
	}
	else {
		this.select(block_id).hide();
	}
}
