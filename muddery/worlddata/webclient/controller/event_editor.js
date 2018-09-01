
/*
 * Derive from the base class.
 */
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";
    this.action_type = "";

    this.action_data_fields = [];
}

EventEditor.prototype = prototype(CommonEditor.prototype);
EventEditor.prototype.constructor = EventEditor;

EventEditor.prototype.init = function() {
    this.trigger_obj = utils.getQueryString("trigger");
    CommonEditor.prototype.init.call(this);
}

EventEditor.prototype.queryFormSuccess = function(data) {
    controller.event_key = "";
    controller.action_type = "";
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            controller.event_key = data[i].value;
            if (!controller.event_key) {
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
    service.queryEventActionData(controller.action_type, controller.event_key, controller.queryActionSuccess, controller.queryActionFailed);
}

EventEditor.prototype.queryAreasFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

EventEditor.prototype.queryActionSuccess = function(data) {
    controller.setActionData(data);
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

    // Bind the event of the type change.
    $("#fields #control-type .form-control").on("change", this.onTypeChanged);

    window.parent.controller.setFrameSize();
}

EventEditor.prototype.onActionChanged = function(e) {
    controller.event_type = $(this).val();
    service.queryEventActionData(controller.action_type, controller.event_key, controller.queryActionSuccess, controller.queryActionFailed);
}

EventEditor.prototype.setActionData = function(data) {
    this.action_data_fields = data.fields;

    $("#event-data").bootstrapTable("destroy");
    $("#event-data").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: utils.parseFields(data.fields),
        data: utils.parseRows(data.fields, data.records),
        sortName: "id",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}
