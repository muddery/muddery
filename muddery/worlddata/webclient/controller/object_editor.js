
/*
 * Derive from the base class.
 */
ObjectEditor = function() {
	CommonEditor.call(this);

    this.object_key = "";
    this.event_fields = [];
}

ObjectEditor.prototype = prototype(CommonEditor.prototype);
ObjectEditor.prototype.constructor = ObjectEditor;


ObjectEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.add_event);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);
}

ObjectEditor.prototype.onImageLoad = function() {
    parent.controller.setFrameSize();
}

ObjectEditor.prototype.onSave = function() {
    // upload images
    var upload_images = false;
    controller.file_fields = [];

    var image_fields = $(".image-input-control");
    for (var i = 0; i < image_fields.length; i++) {
        var file_obj = image_fields[i].files[0];
        if (typeof (file_obj) != "undefined" && file_obj.size > 0) {
            upload_images = true;
            var image_type = $(image_fields[i]).data("image_type");
            var name = $(image_fields[i]).data("field_name");
            controller.file_fields.push(name);
            service.uploadImage(file_obj, name, image_type, controller.uploadSuccess(name), controller.uploadFailed);
        }
    }

    if (!upload_images) {
        controller.saveFields();
    }
}

ObjectEditor.prototype.onEditEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "event";
        var table = "event_data";
        var args = {
            trigger: controller.object_key,
        }
        window.parent.controller.editRecord(editor, table, record_id, args);
    }
}

ObjectEditor.prototype.onDeleteEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteEvent,
                                     {record: record_id});
}

ObjectEditor.prototype.confirmDeleteEvent = function(e) {
    window.parent.controller.hide_waiting();

    var table = controller.table_name;
    var record_id = e.data.record;
    service.deleteRecord(table, record, this.deleteEventSuccess);
}

ObjectEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}

ObjectEditor.prototype.uploadSuccess = function(field_name) {
    var callback = function(data) {
        for (var i = 0; i < controller.file_fields.length; i++) {
            if (controller.file_fields[i] == field_name) {
                controller.file_fields.splice(i, 1);
                var field = $("#control-" + field_name);
                field.find(".editor-control").val(data.resource);
                field.find("img")
                    .attr("src", CONFIG.resource_url + data.resource)
                    .on("load", controller.onImageLoad);
                break;
            }
        }

        if (controller.file_fields.length == 0) {
            controller.saveFields();
        }
    }

    return callback;
}

ObjectEditor.prototype.uploadFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

ObjectEditor.prototype.queryFormSuccess = function(data) {
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            var value = data[i].value;
            if (value) {
                controller.object_key = value;
            }
            else {
                controller.object_key = "";
            }
            break;
        }
    }

    CommonEditor.prototype.queryFormSuccess.call(this, data);
}

ObjectEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
    service.queryObjectEvents(controller.object_key, controller.queryEventTableSuccess, controller.queryEventTableFailed);
}

ObjectEditor.prototype.queryEventTableSuccess = function(data) {
    controller.event_fields = data.fields;

    $("#event-table").bootstrapTable({
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

ObjectEditor.prototype.queryEventTableFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

ObjectEditor.prototype.add_event = function(e) {
    if (!controller.object_key) {
        window.parent.controller.notify("You should save this object first.");
        return;
    }

    var table = "event_data";
    var args = {
        trigger: controller.object_key,
    }
    window.parent.controller.editRecord("event", table, "", args);
}
