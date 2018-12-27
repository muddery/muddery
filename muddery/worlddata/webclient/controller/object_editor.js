
/*
 * Derive from the base class.
 */
ObjectEditor = function() {
	CommonEditor.call(this);

    this.base_typeclass = "";
    this.object_typeclass = "";
    this.object_key = "";
    this.table_fields = [];
    this.event_fields = [];
}

ObjectEditor.prototype = prototype(CommonEditor.prototype);
ObjectEditor.prototype.constructor = ObjectEditor;

ObjectEditor.prototype.init = function() {
    this.base_typeclass = utils.getQueryString("typeclass");
    this.object_key = utils.getQueryString("object");

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.record_id) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.base_typeclass);

    this.bindEvents();
    this.refresh();
}

ObjectEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.addEvent);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);
}

ObjectEditor.prototype.onImageLoad = function() {
    parent.controller.setFrameSize();
}

ObjectEditor.prototype.onSave = function() {
    // Upload images before submit the form.
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
        controller.saveFields(controller.saveFormSuccess, controller.saveFormFailed);
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
    window.parent.controller.hideWaiting();

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

ObjectEditor.prototype.refresh = function() {
    service.queryObjectForm(this.base_typeclass,
                            this.object_typeclass,
                            this.object_key,
                            this.queryFormSuccess,
                            this.queryFormFailed);
}

ObjectEditor.prototype.uploadSuccess = function(field_name) {
    var callback = function(data) {
        // Show images when upload images success.
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

        // Submit the form.
        if (controller.file_fields.length == 0) {
            controller.saveFields(controller.saveFormSuccess, controller.saveFormFailed);
        }
    }

    return callback;
}

ObjectEditor.prototype.uploadFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

ObjectEditor.prototype.queryFormSuccess = function(data) {
    controller.table_fields = data;
    controller.object_typeclass = "";
    controller.object_key = "";

    // get object's typeclass
    for (var t = 0; t < data.length && !controller.object_typeclass; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "typeclass") {
                var value = fields[f].value;
                if (value) {
                    controller.object_typeclass = value;
                }
                break;
            }
        }
    }

    // get object's key
    for (var t = 0; t < data.length && !controller.object_key; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "key") {
                var value = fields[f].value;
                if (value) {
                    controller.object_key = value;
                }
                break;
            }
        }
    }

    // If has area fields.
    var query_areas = false;
    for (var t = 0; t < data.length && !query_areas; t++) {
        for (var f = 0; f < data[t].fields.length; f++) {
            if (data[t].fields[f].type == "Location") {
                query_areas = true;
                break;
            }
        }
    }

    if (query_areas) {
        service.queryAreas(controller.queryAreasSuccess, controller.queryAreasFailed);
    }
    else {
        controller.queryAreasSuccess({});
    }
}

ObjectEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
    service.queryObjectEvents(controller.object_key, controller.queryEventTableSuccess, controller.queryEventTableFailed);
}

ObjectEditor.prototype.queryEventTableSuccess = function(data) {
    controller.event_fields = data.fields;

    $("#event-table").bootstrapTable("destroy");
    $("#event-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: controller.parseFields(data.fields),
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

// Add form fields to the web page.
ObjectEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var t = 0; t < this.table_fields.length; t++) {
        var fields = this.table_fields[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (t == 0 || fields[f].name != "key") {
                // If it is a key field, only add first table's key.
                var controller = this.createFieldController(fields[f]);
                if (controller) {
                    controller.appendTo(container);
                }
            }
        }
    }

    $("#control-typeclass select").on("change", this.onTypeclassChange);
}

ObjectEditor.prototype.onTypeclassChange = function(e) {
    var typeclass = this.value;

    if (controller.object_typeclass != typeclass) {
        controller.object_typeclass = typeclass;
        controller.refresh();
    }
}

ObjectEditor.prototype.saveFields = function(callback_success, callback_failed, context) {
    var tables = [];
    for (var t = 0; t < this.table_fields.length; t++) {
        var fields = this.table_fields[t].fields;
        var values = {};
        for (var f = 0; f < fields.length; f++) {
            var name = fields[f].name;
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
        tables.push({
            table: this.table_fields[t].table,
            values: values
        });
    }

    service.saveObjectForm(tables,
                           this.base_typeclass,
                           this.object_key,
                           callback_success,
                           callback_failed,
                           context);
}

ObjectEditor.prototype.addEvent = function(e) {
    if (!controller.object_key) {
        window.parent.controller.notify("You should save this object first.");
        return;
    }

    var editor = "event";
    var table = "event_data";
    var record = "";
    var args = {
        trigger: controller.object_key,
    }
    window.parent.controller.editRecord(editor, table, record, args);
}
