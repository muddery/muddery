
/*
 * Derive from the base class.
 */
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";
    this.event_type = "";

    this.event_data = [];
}

EventEditor.prototype = prototype(CommonEditor.prototype);
EventEditor.prototype.constructor = EventEditor;

EventEditor.prototype.init = function() {
    this.trigger_obj = getQueryString("trigger");
    CommonEditor.prototype.init.call(this);
}

EventEditor.prototype.queryFormSuccess = function(data) {
    controller.fields = data;

    controller.event_key = "";
    controller.event_type = "";
    var query_areas = false;
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            controller.event_key = data[i].value;
            if (!controller.event_key) {
                controller.event_key = "";
            }
        }
        else if (data[i].name == "type") {
            controller.event_type = data[i].value;
            if (!controller.event_type) {
                // Get default event type.
                if (data[i].choices.length > 0) {
                    controller.event_type = data[i].choices[0][0];
                }
            }
        }
        else if (data[i].type == "Location") {
            query_areas = true;
        }
    }

    if (query_areas) {
        service.queryAreas(controller.queryAreasSuccess, controller.queryAreasFailed);
    }
    else {
        controller.queryAreasSuccess({});
    }
}

EventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
    service.queryEventDataForm(controller.event_type, controller.event_key, controller.queryEventSuccess, controller.queryEventFailed);
}

EventEditor.prototype.queryAreasFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

EventEditor.prototype.queryEventSuccess = function(data) {
    controller.event_data = data;
    controller.setEventData();
}

EventEditor.prototype.queryEventFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

EventEditor.prototype.setFields = function() {
    // Set event fields.
    var event_container = $("#fields");
    event_container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        // Users can not set the event's key and trigger object.
        if (field.name == "key") {
            field.type = "Hidden";
        }
        else if (field.name == "trigger_obj") {
            field.type = "Hidden";
            field.value = this.trigger_obj;
        }

        var controller = this.createFieldController(field);
        if (controller) {
            controller.appendTo(event_container);
        }
    }

    // Bind the event of the type change.
    $("#event_fields #control-type .form-control").on("change", this.onTypeChanged);

    window.parent.controller.setFrameSize();
}

EventEditor.prototype.onTypeChanged = function(e) {
    controller.event_type = $(this).val();
    service.queryEventDataForm(controller.event_type, controller.event_key, controller.queryEventSuccess, controller.queryEventFailed);
}

EventEditor.prototype.setEventData = function(e) {
}
