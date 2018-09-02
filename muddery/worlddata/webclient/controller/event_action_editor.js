
/*
 * Derive from the base class.
 */
EventActionEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
}

EventActionEditor.prototype = prototype(CommonEditor.prototype);
EventActionEditor.prototype.constructor = EventActionEditor;

EventActionEditor.prototype.init = function() {
    this.event_key = utils.getQueryString("event");
    CommonEditor.prototype.init.call(this);
}

EventActionEditor.prototype.setFields = function() {
    // Set fields.
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        // Users can not set the event's key and trigger object.
        if (field.name == "event_key") {
            field.type = "Hidden";
            field.value = this.event_key;
        }

        var controller = this.createFieldController(field);
        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}
