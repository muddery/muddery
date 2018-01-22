//@ sourceURL=/controller/get_objects.js

/*
 * Derive from the base class.
 */
function MudderyGetObjects(root_controller) {
	BaseController.call(this, root_controller);
	
	this.goods = [];
}

MudderyGetObjects.prototype = prototype(BaseController.prototype);
MudderyGetObjects.prototype.constructor = MudderyGetObjects;

/*
 * Reset the view's language.
 */
MudderyGetObjects.prototype.resetLanguage = function() {
	$("#popup_header").text($$("Get Objects"));
	$("#view_get_objects").text($$("Get Objects: "));
	$("#view_rejected").text($$("Can Not Get: "));
	$("#view_button_ok").text($$("OK"));
}

/*
 * Bind events.
 */
MudderyGetObjects.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
    this.onClick("#button_ok", this.onClose);
}

/*
 * Event when clicks the close button.
 */
MudderyGetObjects.prototype.onClose = function(element) {
    $$.controller.doClosePopupBox();
}

/*
 * Set objects that the user get.
 */
MudderyGetObjects.prototype.setObjects = function(accepted, rejected) {
	// set new objects
	this.setItems("#accepted", "#accepted_list", accepted);
	this.setItems("#rejected", "#rejected_list", rejected);
}

/*
 * Set object items.
 */
MudderyGetObjects.prototype.setItems = function(block_id, container_id, objects) {
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
