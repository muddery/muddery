//@ sourceURL=/controller/base_controller.js

var $$;

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
function BaseController(root_controller) {
    if (root_controller) {
        // Common references.
        $$ = root_controller.$$;
    }
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
