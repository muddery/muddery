
/*
 * The event editor.
 * The query sequence:
 * 1. queryForm -> set the event_key and the action_type
 * 2. if need query_areas, queryAreas
 * 3. queryEventTriggers
 * 4. queryEventActionForms
 */

/*
 * Derive from the base class.
 */
ObjectEventEditor = function() {
	EventEditor.call(this);

    this.trigger_element_type = "";
}

ObjectEventEditor.prototype = prototype(EventEditor.prototype);
ObjectEventEditor.prototype.constructor = ObjectEventEditor;

ObjectEventEditor.prototype.init = function() {
    this.trigger_element_type = utils.getQueryString("element_type");
    EventEditor.prototype.init.call(this);
}

ObjectEventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;

    // Query available event trigger types.
    service.queryObjectEventTriggers(controller.trigger_element_type, controller.queryEventTriggersSuccess, controller.failedCallback);
}
