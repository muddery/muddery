
/*
 * The event editor.
 * The query sequence:
 * 1. queryForm -> set the event_key and the action_type
 * 2. if need query_areas, queryAreas
 * 3. queryEventActionForms
 */

/*
 * Derive from the base class.
 */
DialogueEventEditor = function() {
	EventEditor.call(this);
}

DialogueEventEditor.prototype = prototype(EventEditor.prototype);
DialogueEventEditor.prototype.constructor = DialogueEventEditor;

DialogueEventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;

    // Query available event trigger types.
    service.queryDialogueEventTriggers(controller.queryEventTriggersSuccess, controller.failedCallback);
}