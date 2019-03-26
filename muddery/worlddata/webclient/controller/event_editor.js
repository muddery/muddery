
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

    // Action's action data.
    this.action_action_type = "";
    this.action_action_fields = [];
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

        var control = $("#action-fields #control-" + name + " .editor-control");
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
                           this.failedCallback);
}

// The action form has been saved.
EventEditor.prototype.saveActionFormSuccess = function(data) {
    if (controller.action_action_type) {
        controller.saveActionActionFields();
    }
    else {
        controller.exit();
    }
}

/*
 * Save the action's action form.
 */
EventEditor.prototype.saveActionActionFields = function() {
    var values = {};
    for (var i = 0; i < this.action_action_fields.length; i++) {
        var name = this.action_action_fields[i].name;

        if (name == "event_key") {
            // Set the event key.
            values[name] = this.event_key;
            continue;
        }

        var control = $("#action-action-fields #control-" + name + " .editor-control");
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
                           this.action_action_type,
                           this.event_key,
                           this.saveActionActionFormSuccess,
                           this.failedCallback);
}

/*
 * The action's action form has been saved.
 */
EventEditor.prototype.saveActionActionFormSuccess = function(data) {
    controller.exit();
}

EventEditor.prototype.queryFormSuccess = function(data) {
    // Clear old data.
    controller.event_key = "";
    controller.action_type = "";
    controller.action_action_type = "";
    controller.action_fields = [];
    controller.action_action_fields = [];

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
}

EventEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
    service.queryEventActionForm(controller.action_type,
                                 controller.event_key,
                                 controller.queryActionSuccess,
                                 controller.failedCallback);
}

EventEditor.prototype.queryActionSuccess = function(data) {
    controller.setActionFields(data);
}

/*
 * Set fields of the event.
 */
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

        var field_controller = this.createFieldController(field);
        if (field_controller) {
            field_controller.appendTo(event_container);
        }
    }

    // Bind the event of the action change.
    $("#fields #control-action select").on("change", controller.onEventActionChanged);

    window.parent.controller.setFrameSize();
}

/*
 * On the user changed the event's action.
 */
EventEditor.prototype.onEventActionChanged = function(e) {
    controller.action_type = $(this).val();
    service.queryEventActionForm(controller.action_type,
                                 controller.event_key,
                                 controller.queryActionSuccess,
                                 controller.failedCallback);
}

/*
 * Set fields of the event's action.
 */
EventEditor.prototype.setActionFields = function(data) {
    this.action_fields = data;

    // Clear old data.
    this.action_action_type = "";
    this.action_action_fields = [];

    // Clear data fields.
    var container = $("#action-fields");
    container.children().remove();

    $("#action-action-fields").children().remove();

    var action_action = "";
    for (var i = 0; i < this.action_fields.length; i++) {
        if (this.action_fields[i].name == "event_key") {
            // Hide the event key field.
            this.action_fields[i].type = "Hidden";
        }

        var field_controller = this.createFieldController(this.action_fields[i]);
        if (field_controller) {
            field_controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();

    // If this action has actions.
    if (this.action_type == "ACTION_ROOM_INTERVAL") {
        // Bind the event of the action's action change.
        $("#action-fields #control-action select").on("change", controller.onActionActionChanged);

        // Query action's action data.
        for (var i = 0; i < this.action_fields.length; i++) {
            if (this.action_fields[i].name == "action") {
                this.action_action_type = this.action_fields[i].value;
                if (!this.action_action_type) {
                    // Set default event action.
                    if (this.action_fields[i].choices.length > 0) {
                        this.action_action_type = this.action_fields[i].choices[0][0];
                    }
                }

                service.queryEventActionForm(this.action_action_type,
                                             this.event_key,
                                             this.queryActionActionSuccess,
                                             this.failedCallback);
                break;
            }
        }
    }
}

/*
 * On the user changed the action's action.
 */
EventEditor.prototype.onActionActionChanged = function(e) {
    controller.action_action_type = $(this).val();
    service.queryEventActionForm(controller.action_action_type,
                                 controller.event_key,
                                 controller.queryActionActionSuccess,
                                 controller.failedCallback);
}

/*
 * On query action's action data success.
 */
EventEditor.prototype.queryActionActionSuccess = function(data) {
    controller.setActionActionFields(data);
}

/*
 * Set fields of the action's action.
 */
EventEditor.prototype.setActionActionFields = function(data) {
    this.action_action_fields = data;

    var container = $("#action-action-fields");
    container.children().remove();

    for (var i = 0; i < this.action_action_fields.length; i++) {
        if (this.action_action_fields[i].name == "event_key") {
            // Hide the event key field.
            this.action_action_fields[i].type = "Hidden";
        }

        var field_controller = this.createFieldController(this.action_action_fields[i]);
        if (field_controller) {
            field_controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}