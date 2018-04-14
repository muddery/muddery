
/*
 * Get the prototype of the base class.
 */
prototype = function(base, el) {
    var Base = function(){};
    Base.prototype = base;
    return new Base(el);
}


////////////////////////////////////////
//
// The base of view controllers.
//
////////////////////////////////////////

/*
 * The base controller's constructor.
 */
BaseController = function(el) {
    this.el = el;
}

/*
 * Find DOM.
 */
BaseController.prototype.select = function(selector) {
    return this.el.find(selector);
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
 * Show the element.
 */
BaseController.prototype.show = function() {
    this.el.show();
    this.el.parents().show();
	this.resetSize();
}

/*
 * Is visible.
 */
BaseController.prototype.visible = function() {
    return this.el.is(":visible");
}

/*
 * Set element's size.
 */
BaseController.prototype.resetSize = function() {
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

	this.select(element_name).on(event_name, selector, this, function(event) {
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
    
	this.select(element_name).off(event_name, selector);
}

/*
 * Clone a template tag.
 */
BaseController.prototype.cloneTag = function(tag, root) {
	if (root) {
        var template = root.children(tag + ".template");
    }
    else {
    	var template = this.select(tag + ".template");
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
	this.select(root_tag).children().not(".template").remove();
}


////////////////////////////////////////
//
// The base of popup controllers.
//
////////////////////////////////////////
 /*
 * Derive from the base class.
 */
BasePopupController = function(el) {
	BaseController.call(this, el);
	
	this.target = null;
}

BasePopupController.prototype = prototype(BaseController.prototype);
BasePopupController.prototype.constructor = BasePopupController;

/*
 * Set element's size.
 */
BasePopupController.prototype.resetSize = function() {
	$$.main.doSetVisiblePopupSize();
}


////////////////////////////////////////
//
// The base of tab controllers.
//
////////////////////////////////////////
 /*
 * Derive from the base class.
 */
BaseTabController = function(el) {
	BaseController.call(this, el);

	this.target = null;
}

BaseTabController.prototype = prototype(BaseController.prototype);
BaseTabController.prototype.constructor = BaseTabController;

/*
 * Set element's size.
 */
BaseTabController.prototype.resetSize = function() {
	var tab_content = $("#tab_content");

	this.el.width(tab_content.width());
	this.el.height(tab_content.height() - 5);
}