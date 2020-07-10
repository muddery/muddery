
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
BaseController.prototype.init = function() {
    this.bindEvents();
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
 * Hide the element.
 */
BaseController.prototype.hide = function() {
    this.el.hide();
}

/*
 * Reset the element.
 */
BaseController.prototype.reset = function() {
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
    if (typeof(selector) === "function") {
    	method = selector;
    	event_name = element_name;
    	element_name = undefined;
    	selector = undefined;
    }
    else if (typeof(event_name) === "function") {
    	method = event_name;
    	event_name = selector;
    	selector = undefined;
    }

    if (!element_name) {
        this.el.on(event_name, selector, this, function(event) {
            method.call(event.data, event.currentTarget, event);
        });
    }
	else {
	    this.select(element_name).on(event_name, selector, this, function(event) {
            method.call(event.data, event.currentTarget, event);
        });
    }
}

/*
 * Bind a click event to an element with an object method.
 */
BaseController.prototype.onClick = function(element_name, selector, method) {
    if (typeof(element_name) === "function") {
        method = element_name;
        element_name = undefined;
    	selector = undefined;
    }
	else if (typeof(selector) === "function") {
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

