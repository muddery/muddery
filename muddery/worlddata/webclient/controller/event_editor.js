
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
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";
    this.trigger_typeclass = "";

    // Action's data.
    this.action_type = "";
    this.actions = [];

    // Action's action data.
    this.action_action_type = "";
    this.action_actions = [];
}

EventEditor.prototype = prototype(CommonEditor.prototype);
EventEditor.prototype.constructor = EventEditor;

EventEditor.prototype.init = function() {
    this.trigger_obj = utils.getQueryString("trigger");
    this.trigger_typeclass = utils.getQueryString("typeclass");
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
    controller.saveActionForms();
}

// Save the action forms.
EventEditor.prototype.saveActionForms = function() {
    var action_value_list = []
    var action_blocks = $(".action-block");

    for (var b = 0; b < action_blocks.length; b++) {
        var values = {};
        var action_fields = $(action_blocks[b]).find(".field-controller");
        for (var f = 0; f < action_fields.length; f++) {
            var name = $(action_fields[f]).data("field-name");

            if (name == "event_key") {
                // Set the event key.
                values[name] = this.event_key;
                continue;
            }

            var control = $(action_fields[f]).find(".editor-control");
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
        action_value_list.push(values);
    }

    service.saveEventActionForms(action_value_list,
                                this.action_type,
                                this.event_key,
                                this.saveActionFormsSuccess,
                                this.failedCallback);
}

// The action form has been saved.
EventEditor.prototype.saveActionFormsSuccess = function(data) {
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
    var container = $(".action-action-fields");

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

    service.saveEventActionForms(values,
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

    // Query available event trigger types.
    service.queryEventTriggers(controller.trigger_typeclass, controller.queryEventTriggersSuccess, controller.failedCallback);
}

EventEditor.prototype.queryEventTriggersSuccess = function(data) {
    // Set available triggers.
    var trigger_types = data;
    for (var i = 0; i < controller.fields.length; i++) {
        var field = controller.fields[i];
        if (field.name == "trigger_type") {
            var choices = [];
            for (var j = 0; j < field.choices.length; j++) {
                if (trigger_types.indexOf(field.choices[j][0]) >= 0) {
                    choices.push(field.choices[j]);
                }
            }
            field.choices = choices;
        }
    }

    controller.setFields();

    // Query actions.
    service.queryEventActionForms(controller.action_type,
                                  controller.event_key,
                                  controller.queryActionSuccess,
                                  controller.failedCallback);
}

EventEditor.prototype.queryActionSuccess = function(data) {
    // Clear old data.
    controller.action_action_type = "";
    controller.action_actions = [];

    // Clear data fields.
    var container = $("#action-forms");
    container.children().remove();

    // Set new forms.
    var forms = data.forms;
    for (var i = 0; i < forms.length; i++) {
        controller.addActionForm(forms[i], container);
    }

    if (forms.length == 1) {
        // If there is only one action left, hide the delete button.
        $(".action-block .btn-delete").hide();
    }
    if (data.repeatedly) {
        // Repeatable actions, add an add button.
        var button = $("<button>")
            .attr("type", "button")
            .addClass("btn btn-default btn-add-action")
            .text("Add Action")
            .on("click", this.onAddAction)
            .appendTo(container);
    }

    window.parent.controller.setFrameSize();

    // Show action's action fields.
    controller.showActionAction();
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
    $("#fields .control-item-action select").on("change", controller.onEventActionChanged);

    window.parent.controller.setFrameSize();
}


/*
 * Show action's action.
 */
EventEditor.prototype.showActionAction = function() {
    return;

    // If this action has actions.
    if (this.action_type == "ACTION_ROOM_INTERVAL") {
        // Bind the event of the action's action change.
        $(".action-block .control-item-action select").on("change", controller.onActionActionChanged);

        // Query action's action data.
        for (var i = 0; i < this.actions[0].length; i++) {
            if (this.actions[0][i].name == "action") {
                this.action_action_type = this.actions[0][i].value;
                if (!this.action_action_type) {
                    // Set default event action.
                    if (this.actions[0][i].choices.length > 0) {
                        this.action_action_type = this.actions[0][i].choices[0][0];
                    }
                }

                service.queryEventActionForms(this.action_action_type,
                                              this.event_key,
                                              this.queryActionActionSuccess,
                                              this.failedCallback);
                break;
            }
        }
    }
}

/*
 * On the user changed the event's action.
 */
EventEditor.prototype.onEventActionChanged = function(e) {
    controller.action_type = $(this).val();
    service.queryEventActionForms(controller.action_type,
                                  controller.event_key,
                                  controller.queryActionSuccess,
                                  controller.failedCallback);
}

/*
 * Set a form of the event's action.
 */
EventEditor.prototype.addActionForm = function(data, container) {
    var block = $("<div>")
        .addClass("block action-block")
        .appendTo(container);

    var title = $("<h4>")
        .addClass("action-title")
        .text("Action Data")
        .appendTo(block);

    var button = $("<button>")
        .attr("type", "button")
        .addClass("btn btn-sm btn-default btn-delete")
        .text("Delete")
        .on("click", this.onDeleteAction)
        .appendTo(block);

    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "event_key") {
            // Hide the event key field.
            data[i].type = "Hidden";
        }

        var field_controller = this.createFieldController(data[i]);
        if (field_controller) {
            field_controller.appendTo(block);
        }
    }
}

/*
 * On the user changed the action's action.
 */
EventEditor.prototype.onActionActionChanged = function(e) {
    controller.action_action_type = $(this).val();
    service.queryEventActionForms(controller.action_action_type,
                                  controller.event_key,
                                  controller.queryActionActionSuccess,
                                  controller.failedCallback);
}

/*
 * On query action's action data success.
 */
EventEditor.prototype.queryActionActionSuccess = function(data) {
    controller.action_actions = data;

    // Clear data fields.
    $(".action-action-title").remove();
    $(".action-action-block").remove();

    var title = $("<h4>")
        .addClass("action-title action-action-title")
        .text("Data")
        .appendTo($(".action-block"));

    var block = $("<div>")
        .addClass("block action-action-block")
        .appendTo($(".action-block"));

    for (var i = 0; i < data.length; i++) {
        controller.setActionFields(data[i], block);
    }

    window.parent.controller.setFrameSize();
}

/*
 * On users click the delete action button.
 */
EventEditor.prototype.onDeleteAction = function(e) {

}