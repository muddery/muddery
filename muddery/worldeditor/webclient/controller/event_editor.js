
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
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";

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
    if (!controller.event_key) {
        // Set the event's key.
        for (var i = 0; i < data.length; i++) {
            if (data[i].name == "key") {
                controller.event_key = data[i].value;
                break;
            }
        }
    }
    controller.saveActionForms();
}

// Save the action forms.
EventEditor.prototype.saveActionForms = function() {
    var action_value_list = []
    var action_blocks = $("#action-forms .action-block");

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
        controller.saveActionActionForms();
    }
    else {
        controller.exit();
    }
}

/*
 * Save the action's action form.
 */
EventEditor.prototype.saveActionActionForms = function() {
    var action_value_list = []
    var action_blocks = $("#action-action-forms .action-action-block");

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
                                this.action_action_type,
                                this.event_key,
                                this.saveActionActionFormsSuccess,
                                this.failedCallback);
}

/*
 * The action's action form has been saved.
 */
EventEditor.prototype.saveActionActionFormsSuccess = function(data) {
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

EventEditor.prototype.queryActionSuccess = function(data) {
    controller.actions = data;

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

    // Repeatable actions, show the add action button.
    if (data.repeatedly) {
        $("#add-action").removeClass("hidden");
    }
    else {
        $("#add-action").addClass("hidden");
    }

    window.parent.controller.setFrameSize();

    // Show action's action fields.
    controller.showActionAction();
}

/*
 * Show action's action.
 */
EventEditor.prototype.showActionAction = function() {
    // If this action has actions.
    if (this.action_type == "ACTION_ROOM_INTERVAL") {
        // Bind the event of the action's action change.
        $(".action-block .control-item-action select").on("change", controller.onActionActionChanged);

        // Query action's action data.
        for (var i = 0; i < this.actions.forms[0].length; i++) {
            var field = this.actions.forms[0][i];
            if (field.name == "action") {
                this.action_action_type = field.value;
                if (!this.action_action_type) {
                    // Set default event action.
                    if (field.choices.length > 0) {
                        this.action_action_type = field.choices[0][0];
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
    $("#action-action-forms").remove();
    $("#add-action-action").remove();

    var container = $("<div>")
        .attr("id", "action-action-forms")
        .appendTo(".action-block");

    // Set new forms.
    var forms = data.forms;
    for (var i = 0; i < forms.length; i++) {
        controller.addActionActionForm(forms[i], container);
    }

    if (forms.length == 1) {
        // If there is only one action left, hide the delete button.
        $(".action-action-block .btn-delete").hide();
    }

    // Repeatable actions, show the add action button.
    if (data.repeatedly) {
        var button = $("<button>")
            .attr("id", "add-action-action")
            .attr("type", "button")
            .addClass("btn btn-default")
            .text("Add Action")
            .on("click", controller.onAddActionAction)
            .appendTo($(".action-block"));
    }

    window.parent.controller.setFrameSize();
}

/*
 * Set a form of the action's action.
 */
EventEditor.prototype.addActionActionForm = function(data, container) {
    var block = $("<div>")
        .addClass("block action-action-block")
        .appendTo(container);

    var title = $("<h4>")
        .addClass("action-title")
        .text("Data")
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
 * On users click the add action button.
 */
EventEditor.prototype.onAddAction = function(e) {
    // Query a new action.
    service.queryEventActionForms(controller.action_type,
                                  "",
                                  controller.queryNewActionSuccess,
                                  controller.failedCallback);
}

EventEditor.prototype.queryNewActionSuccess = function(data) {
    // Clear data fields.
    var container = $("#action-forms");

    // Set new forms.
    var forms = data.forms;
    for (var i = 0; i < forms.length; i++) {
        controller.addActionForm(forms[i], container);
    }

    $(".action-block .btn-delete").show();

    window.parent.controller.setFrameSize();
}

/*
 * On users click the delete action button.
 */
EventEditor.prototype.onDeleteAction = function(e) {
    var to_delete = $(this).parent();
    window.parent.controller.confirm("",
                                     "Delete this action?",
                                     function() {
                                         window.parent.controller.hideWaiting();
                                         to_delete.remove();
                                     });
}

/*
 * On users click the add action action button.
 */
EventEditor.prototype.onAddActionAction = function(e) {
    // Query a new action.
    service.queryEventActionForms(controller.action_action_type,
                                  "",
                                  controller.queryNewActionActionSuccess,
                                  controller.failedCallback);
}

EventEditor.prototype.queryNewActionActionSuccess = function(data) {
    // Clear data fields.
    var container = $("#action-action-forms");

    // Set new forms.
    var forms = data.forms;
    for (var i = 0; i < forms.length; i++) {
        controller.addActionActionForm(forms[i], container);
    }

    $(".action-action-block .btn-delete").show();

    window.parent.controller.setFrameSize();
}
