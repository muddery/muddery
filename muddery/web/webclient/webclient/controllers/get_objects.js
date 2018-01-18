//@ sourceURL=/controller/get_objects.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
	this.goods = [];
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#popup_header").text($$("Get Objects"));
	$("#view_get_objects").text($$("Get Objects: "));
	$("#view_rejected").text($$("Can Not Get: "));
	$("#view_button_ok").text($$("OK"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
	$("#button_ok").bind("click", this.onClose);
}

/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function(event) {
    $$.controller.doClosePopupBox();
}

/*
 * Set objects that the user get.
 */
Controller.prototype.setObjects = function(accepted, rejected) {
	// set new objects
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