
/*
 * The event editor.
 * The query sequence:
 * 1. queryForm -> set the event_key and the action_type
 * 2. if need query_areas, queryAreas
 * 3. queryEventTriggers
 * 4. queryEventActionForms
 * 5. if the action_type is "ACTION_ROOM_INTERVAL", use queryEventActionForms to query interval actions.
 */

/*
 * Derive from the base class.
 */
ObjectEventEditor = function() {
	EventEditor.call(this);

    this.trigger_typeclass = "";
}

ObjectEventEditor.prototype = prototype(EventEditor.prototype);
ObjectEventEditor.prototype.constructor = ObjectEventEditor;

ObjectEventEditor.prototype.init = function() {
    this.trigger_typeclass = utils.getQueryString("typeclass");
    EventEditor.prototype.init.call(this);
}

ObjectEventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;

    // Query available event trigger types.
    service.queryObjectEventTriggers(controller.trigger_typeclass, controller.queryEventTriggersSuccess, controller.failedCallback);
}
