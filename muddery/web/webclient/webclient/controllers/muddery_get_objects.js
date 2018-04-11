
/*
 * Derive from the base class.
 */
function MudderyGetObjects(el) {
	BaseController.call(this, el);
	
	this.goods = [];
}

MudderyGetObjects.prototype = prototype(BaseController.prototype);
MudderyGetObjects.prototype.constructor = MudderyGetObjects;

/*
 * Reset the view's language.
 */
MudderyGetObjects.prototype.resetLanguage = function() {
	this.select("#get_obj_popup_header").text($$("Get Objects"));
	this.select("#get_obj_view_get_objects").text($$("Get Objects: "));
	this.select("#get_obj_view_rejected").text($$("Can Not Get: "));
	this.select("#get_obj_view_button_ok").text($$("OK"));
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
    $$.controller.doClosePopupBox();
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
