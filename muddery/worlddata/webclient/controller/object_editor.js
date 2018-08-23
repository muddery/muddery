
/*
 * Derive from the base class.
 */
ObjectEditor = function() {
	CommonEditor.call(this);

    this.object_key = "";
}

ObjectEditor.prototype = prototype(CommonEditor.prototype);
ObjectEditor.prototype.constructor = ObjectEditor;


ObjectEditor.prototype.init = function() {
    this.table_name = getQueryString("table");
    this.record_id = getQueryString("record");
    this.fields = [];

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.record_id) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.table_name);

    this.bindEvents();

    service.queryForm(this.table_name, this.record_id, this.queryFormSuccess, this.queryFormFailed);
}

ObjectEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.add_event);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);
}

ObjectEditor.prototype.onImageLoad = function() {
    parent.controller.setFrameSize();
}

ObjectEditor.prototype.onExit = function() {
    controller.exit_no_change();
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
    var record_id = $(this).attr("data-event-id");
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
    var record_id = $(this).attr("data-event-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete,
                                     {record: record_id});
}

ObjectEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hide_waiting();

    var table = controller.table_name;
    var record_id = e.data.record;
    controller.deleteRecord(table, record_id);
},

ObjectEditor.prototype.deleteRecord = function(table, record) {
    service.deleteRecord(table, record, this.deleteSuccess);
},

ObjectEditor.prototype.deleteSuccess = function(data) {
    var record_id = data.record;
    $("#data-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
},

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
    CommonEditor.prototype.queryFormSuccess.call(this, data);

    if (data.hasOwnProperty("events")) {
        controller.setEvents(data.events);
    }

    $(window).resize();
    parent.controller.setFrameSize();
}

ObjectEditor.prototype.setFields = function(fields) {
    // Get object's key
    for (var i = 0; i < fields.length; i++) {
        if (fields[i].name == "key") {
            this.object_key = fields[i].value;
            break;
        }
    }

    CommonEditor.prototype.setFields.call(this, fields);
}

ObjectEditor.prototype.setEvents = function(events) {
    var table = $("#event-table");
    if (events.length > 0) {
        table.find("tr:not(:first)").remove();
    }

    for (var i = 0; i < events.length; i++) {
        var line = $("<tr>")
            .append($("<td>").text(events[i].trigger_type))
            .append($("<td>").text(events[i].event_type))
            .append($("<td>").text(events[i].one_time))
            .append($("<td>").text(events[i].odds))
            .append($("<td>").text(events[i].condition));

        var operations = $("<td>")
            .appendTo(line);

        $("<button>")
            .addClass("btn-xs edit-row")
            .attr("type", "button")
            .attr("data-event-id", events[i].id)
            .text("Edit")
            .appendTo(operations);

        $("<button>")
            .addClass("btn-xs btn-danger delete-row")
            .attr("type", "button")
            .attr("data-event-id", events[i].id)
            .text("Delete")
            .appendTo(operations);

        line.appendTo(table);
    }
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
