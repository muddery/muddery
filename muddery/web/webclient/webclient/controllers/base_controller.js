//@ sourceURL=/controller/base_controller.js

/*
 * Get the prototype of the base class.
 */
function prototype(base) {
    var Base = function(){};
    Base.prototype = base;
    return new Base();
}

/*
 * The base of view controllers.
 */
function BaseController() {
}

/*
 * Document ready event.
 */
BaseController.prototype.onReady = function() {
    this.resetLanguage();
    this.bindEvents();
}

/*
 * Reset the view's language.
 */
BaseController.prototype.resetLanguage = function() {
}

/*
 * Bind events.
 */
BaseController.prototype.bindEvents = function() {
}

/*
 * Bind an event to an element with an object method.
 * on(element_name [,selector] , event_name, method)
 */
BaseController.prototype.on = function(element_name, selector, event_name, method) {
    if (typeof(event_name) === "function") {
    	method = event_name;
    	event_name = selector;
    	selector = undefined;
    }

	$(element_name).on(event_name, selector, this, function(event) {
		method.call(event.data, event.currentTarget, event);
	});
}

/*
 * Bind a click event to an element with an object method.
 */
BaseController.prototype.onClick = function(element_name, selector, method) {
	if (typeof(selector) === "function") {
    	method = selector;
    	selector = undefined;
    }
    
	this.on(element_name, selector, "click", method);
}

/*
 * Unbind an event to an element with an object method.
 * off(element_name [,selector] [,event_name])
 */
BaseController.prototype.off = function(element_name, selector, event_name) {
    if (typeof(event_name) === "undefined") {
    	event_name = selector;
    	selector = undefined;
    }
    
	$(element_name).off(event_name, selector);
}

/*
 * Clone a template tag.
 */
BaseController.prototype.cloneTag = function(tag, root) {
	if (root) {
        var template = root.children(tag + ".template");
    }
    else {
    	var template = $(tag + ".template");
    }
    this.cloneTemplate(tempalte);
}

/*
 * Clone a template elements.
 */
BaseController.prototype.cloneTemplate = function(template) {
	var item = template.clone().removeClass("template");
	item.appendTo(template.parent());
	return item;
}

/*
 * Clear cloned elements.
 */
BaseController.prototype.clearElements = function(root_tag) {
    // Remove elements that are not template.
	$(root_tag).children().not(".template").remove();
}
