
/*
 * Derive from the base class.
 */
EventEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
    this.trigger_obj = "";
    this.action_type = "";
    this.action_table = "";

    this.action_data_fields = [];
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
    
    // Bind events
    $("#control-action select").on("change", controller.onActionChanged);
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

    // Bind the event of the action change.
    $("#fields #control-action .form-control").on("change", this.onTypeChanged);

    window.parent.controller.setFrameSize();
}

EventEditor.prototype.onActionChanged = function(e) {
    controller.action_type = $(this).val();
    service.queryEventActionData(controller.action_type, controller.event_key, controller.queryActionSuccess, controller.queryActionFailed);
}

EventEditor.prototype.setActionData = function(data) {
    if (!data) {
        // No action data, hide the action table.
        $("#action-table").hide();
    }

    this.action_table = data.table;
    this.action_data_fields = data.fields;

    $("#action-table").bootstrapTable("destroy");
    $("#action-table").bootstrapTable({
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
    $("#action-table").show();

    window.parent.controller.setFrameSize();
}

EventEditor.prototype.onAddAction = function(e) {
    controller.saveFields(controller.addAction, controller.saveFormFailed);
}

EventEditor.prototype.addAction = function() {
    if (!controller.event_key) {
        window.parent.controller.notify("You should save this object first.");
        return;
    }

    var editor = "event_action";
    var table = controller.action_table;
    var record = "";
    var args = {
        event: controller.event_key,
    }
    window.parent.controller.editRecord(editor, controller.action_table, record, args);
}

EventEditor.prototype.onEditAction = function(e) {
    var context = {
        record_id: $(this).attr("data-record-id"),
    }
    
    controller.saveFields(controller.editActionSuccess, controller.saveFormFailed, context);
}

EventEditor.prototype.editActionSuccess = function(data, context) {
    var record_id = context.record_id;
    if (record_id) {
        var editor = "event_action";
        var table = controller.action_table;
        var args = {
            event: controller.event_key,
        }
        window.parent.controller.editRecord(editor, controller.action_table, record_id, args);
    }
}

EventEditor.prototype.onDeleteAction = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteAction,
                                     {record: record_id});
}

EventEditor.prototype.confirmDeleteAction = function(e) {
    window.parent.controller.hideWaiting();

    var table = controller.action_table;
    var record_id = e.data.record;
    service.deleteRecord(table, record, this.deleteActionSuccess);
}

EventEditor.prototype.deleteActionSuccess = function(data) {
    var record_id = data.record;
    $("#action-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}
