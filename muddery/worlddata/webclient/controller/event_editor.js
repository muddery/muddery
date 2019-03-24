
/*
 * Derive from the base class.
 */
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";

    // Action's data.
    this.action_type = "";
    this.action_fields = [];
}

EventEditor.prototype = prototype(CommonEditor.prototype);
EventEditor.prototype.constructor = EventEditor;

EventEditor.prototype.init = function() {
    this.trigger_obj = utils.getQueryString("trigger");
    CommonEditor.prototype.init.call(this);
}

EventEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-action").on("click", this.onAddAction);
    $("#action-table").on("click", ".edit-row", this.onEditAction);
    $("#action-table").on("click", ".delete-row", this.onDeleteAction);
}

// The event form has been saved.
EventEditor.prototype.saveFormSuccess = function(data) {
    controller.event_key = "";
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            controller.event_key = data[i].value;
            if (!controller.event_key) {
                // Set the event's key.
                controller.event_key = "";
            }
            break;
        }
    }
    controller.saveActionFields();
}

// Save the action form.
EventEditor.prototype.saveActionFields = function() {
    var values = {};
    for (var i = 0; i < this.action_fields.length; i++) {
        var name = this.action_fields[i].name;

        if (name == "event_key") {
            // Set the event key.
            values[name] = this.event_key;
            continue;
        }

        var control = $("#control-" + name + " .editor-control");
        if (control.length > 0) {
            if (control.attr("type") == "checkbox") {
                values[name] = control.prop("checked");
            }
            else {
                // Leave the value blank if it is an empty string.
                var value = control.val();
                if (value.length > 0) {
                    values[name] = value;
                }
            }
        }
    }

    service.saveActionForm(values,
                           this.action_type,
                           this.event_key,
                           this.saveActionFormSuccess,
                           this.saveFormFailed);
}

// The action form has been saved.
EventEditor.prototype.saveActionFormSuccess = function(data) {
    controller.exit();
}

EventEditor.prototype.queryFormSuccess = function(data) {
    controller.event_key = "";
    controller.action_type = "";
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            controller.event_key = data[i].value;
            if (!controller.event_key) {
                // Set the event's key.
                controller.event_key = "";
            }
        }
        else if (data[i].name == "action") {
            controller.action_type = data[i].value;
            if (!controller.action_type) {
                // Set default event action.
                if (data[i].choices.length > 0) {
                    controller.action_type = data[i].choices[0][0];
                }
            }
        }
    }

    CommonEditor.prototype.queryFormSuccess.call(this, data);
    
    // Bind events
    $("#control-action select").on("change", controller.onActionChanged);
}

EventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
    service.queryEventActionForm(controller.action_type,
                                 controller.event_key,
                                 controller.queryActionSuccess,
                                 controller.queryActionFailed);
}

EventEditor.prototype.queryAreasFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

EventEditor.prototype.queryActionSuccess = function(data) {
    controller.setActionForm(data);
}

EventEditor.prototype.queryActionFailed = function(code, message, data) {
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

    // Bind the event of the action change.
    $("#fields #control-action .form-control").on("change", this.onTypeChanged);

    window.parent.controller.setFrameSize();
}

// On the user selected another action.
EventEditor.prototype.onActionChanged = function(e) {
    controller.action_type = $(this).val();
    service.queryEventActionForm(controller.action_type,
                                 controller.event_key,
                                 controller.queryActionSuccess,
                                 controller.queryActionFailed);
}

// Add the action's form to the web page.
EventEditor.prototype.setActionForm = function(data) {
    this.action_fields = data;

    var container = $("#action-fields");
    container.children().remove();

    for (var i = 0; i < this.action_fields.length; i++) {
        if (this.action_fields[i].name == "event_key") {
            // Hide the event key field.
            this.action_fields[i].type = "Hidden";
        }

        var controller = this.createFieldController(this.action_fields[i]);
        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}
