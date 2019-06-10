
/*
 * Derive from the base class.
 */
ObjectEditor = function() {
	CommonEditor.call(this);

    this.base_typeclass = "";
    this.obj_typeclass = "";
    this.obj_key = "";
    this.table_fields = [];

    this.event_fields = [];
    this.event_table = "event_data";

    this.properties_fields = [];
    this.properties_table = "object_properties"
}

ObjectEditor.prototype = prototype(CommonEditor.prototype);
ObjectEditor.prototype.constructor = ObjectEditor;

ObjectEditor.prototype.init = function() {
    this.base_typeclass = utils.getQueryString("typeclass");
    this.obj_key = utils.getQueryString("object");
    this.no_delete = utils.getQueryString("no_delete");

    if (sessionStorage.page_param) {
        this.field_values = JSON.parse(sessionStorage.page_param);
    }
    else {
        this.field_values = {};
    }

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.obj_key && !this.no_delete) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.base_typeclass);

    this.bindEvents();
    this.refresh();
}


/***********************************
 *
 * Events
 *
 ***********************************/
ObjectEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.onAddEvent);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);

    $("#add-properties").on("click", this.onAddProperties);
    $("#properties-table").on("click", ".edit-row", this.onEditProperties);
    $("#properties-table").on("click", ".delete-row", this.onDeleteProperties);
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
        if (file_obj && file_obj.size > 0) {
            upload_images = true;
            var image_type = $(image_fields[i]).data("image_type");
            var name = $(image_fields[i]).data("field_name");
            controller.file_fields.push(name);
            service.uploadImage(file_obj, name, image_type, controller.uploadSuccess(name), controller.failedCallback);
        }
    }

    if (!upload_images) {
        controller.saveForm(controller.saveFormSuccess, controller.saveFormFailed, {container: "#fields"});
    }
}

ObjectEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    service.deleteObject(controller.obj_key,
                         controller.base_typeclass,
                         controller.deleteSuccess,
                         controller.failedCallback);
}


ObjectEditor.prototype.addEvent = function(e) {
    if (!controller.obj_key) {
        window.parent.controller.notify("You should save this object first.");
        return;
    }

    var editor = "event";
    var record = "";
    var args = {
        trigger: controller.obj_key,
        typeclass: controller.obj_typeclass,
    }
    window.parent.controller.editRecord(editor, controller.event_table, record, args);
}

ObjectEditor.prototype.onEditEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "event";
        var args = {
            trigger: controller.obj_key,
             typeclass: controller.obj_typeclass,
        }
        window.parent.controller.editRecord(editor, controller.event_table, record_id, args);
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

    var record_id = e.data.record;
    service.deleteRecord(controller.event_table, record_id, controller.deleteEventSuccess, controller.failedCallback);
}

ObjectEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}

ObjectEditor.prototype.onAddProperties = function(e) {
    if (!controller.obj_key) {
        window.parent.controller.notify("You should save this object first.");
        return;
    }

    window.parent.controller.editObjectProperties(controller.obj_key, null);
}

ObjectEditor.prototype.onEditProperties = function(e) {
    var level = $(this).attr("data-level");
    if (level) {
        window.parent.controller.editObjectProperties(controller.obj_key, level);
    }
}

ObjectEditor.prototype.onDeleteProperties = function(e) {
    var level = $(this).attr("data-level");
    window.parent.controller.confirm("",
                                     "Delete this level?",
                                     controller.confirmDeleteProperties,
                                     {level: level});
}

ObjectEditor.prototype.confirmDeleteProperties = function(e) {
    window.parent.controller.hideWaiting();

    var level = e.data.level;
    service.deleteObjectLevelProperties(controller.obj_key, level, controller.deletePropertiesSuccess, controller.failedCallback);
}

ObjectEditor.prototype.deletePropertiesSuccess = function(data) {
    var level = parseInt(data.level);
    $("#properties-table").bootstrapTable("remove", {
        field: "level",
        values: [level],
    });
}


/***********************************
 *
 * Queries.
 *
 ***********************************/
ObjectEditor.prototype.refresh = function() {
    // Query object form.
    service.queryObjectForm(this.base_typeclass,
                            this.obj_typeclass,
                            this.obj_key,
                            this.queryFormSuccess,
                            this.failedCallback);
}

ObjectEditor.prototype.uploadSuccess = function(field_name) {
    var callback = function(data) {
        var container = $("#fields");
        // Show images when upload images success.
        for (var i = 0; i < controller.file_fields.length; i++) {
            if (controller.file_fields[i] == field_name) {
                controller.file_fields.splice(i, 1);
                var field = container.find(".control-item-" + field_name);
                field.find(".editor-control").val(data.resource);
                field.find("img")
                    .attr("src", CONFIG.resource_url + data.resource)
                    .on("load", controller.onImageLoad);
                break;
            }
        }

        // Submit the form.
        if (controller.file_fields.length == 0) {
            controller.saveForm(controller.saveFormSuccess, controller.saveFormFailed, {container: "#fields"});
        }
    }

    return callback;
}

ObjectEditor.prototype.queryFormSuccess = function(data) {
    controller.table_fields = data;
    controller.obj_typeclass = "";
    controller.obj_key = "";

    // Get object's typeclass.
    for (var t = 0; t < data.length && !controller.obj_typeclass; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "typeclass") {
                var value = fields[f].value;
                if (value) {
                    controller.obj_typeclass = value;
                }
                break;
            }
        }
    }

    // Get object's key.
    for (var t = 0; t < data.length && !controller.obj_key; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "key") {
                var value = fields[f].value;
                if (value) {
                    controller.obj_key = value;
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

    // Query events.
    service.queryEventTriggers(controller.obj_typeclass,
                               controller.queryEventTriggersSuccess,
                               controller.failedCallback);

    service.queryObjectEvents(controller.obj_key,
                              controller.queryEventTableSuccess,
                              controller.failedCallback);

    // Query custom properties.
    service.queryObjectProperties(controller.obj_key,
                                  controller.queryObjectPropertiesSuccess,
                                  controller.failedCallback);
}

ObjectEditor.prototype.queryEventTriggersSuccess = function(data) {
    // If can have events, show the events block.
    if (data && data.length > 0) {
        $("#events").show();
    }
    else {
        $("#events").hide();
    }
    window.parent.controller.setFrameSize();
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

ObjectEditor.prototype.queryObjectPropertiesSuccess = function(data) {
    controller.properties_fields = data.fields;

    $("#properties-table").bootstrapTable("destroy");
    $("#properties-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: controller.propertiesFields(data.fields),
        data: utils.parseRows(data.fields, data.records),
        sortName: "id",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}

// Add form fields to the web page.
ObjectEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var t = 0; t < this.table_fields.length; t++) {
        var fields = this.table_fields[t].fields;
        var block = $("<div>")
            .addClass("table-block")
            .data("table-name", this.table_fields[t].table)
            .appendTo(container);

        for (var f = 0; f < fields.length; f++) {
            var field = fields[f];

            if (t != 0 && field.name == "key") {
                // If it is a key field, only add the first table's key.
                field.type = "Hidden";
            }

            var controller = this.createFieldController(field);
            if (controller) {
                controller.appendTo(block);
            }
        }
    }

    container.find(".control-item-typeclass select").on("change", this.onTypeclassChange);

    window.parent.controller.setFrameSize();
}

ObjectEditor.prototype.onTypeclassChange = function(e) {
    var typeclass = this.value;

    if (controller.obj_typeclass != typeclass) {
        controller.obj_typeclass = typeclass;
        controller.refresh();
    }
}

ObjectEditor.prototype.saveForm = function(callback_success, callback_failed, context) {
    var table_blocks = $("#fields .table-block");
    var key = "";
    var tables = [];
    for (var t = 0; t < table_blocks.length; t++) {
        var table_name = $(table_blocks[t]).data("table-name");
        var fields = $(table_blocks[t]).find(".field-controller");
        var values = {};
        for (var f = 0; f < fields.length; f++) {
            var name = $(fields[f]).data("field-name");
            var control = $(fields[f]).find(".editor-control");
            if (control.length > 0) {
                if (control.attr("type") == "checkbox") {
                    values[name] = control.prop("checked");
                }
                else {
                    // Leave the value blank if it is an empty string.
                    var value = control.val();
                    if (value.length > 0) {
                        values[name] = value;

                        // Get the object's key.
                        if (!key && name == "key") {
                            key = value;
                        }
                    }
                }
            }
        }
        tables.push({
            table: table_name,
            values: values
        });
    }

    // Set the key to all tables.
    for (var t = 0; t < tables.length; t++) {
        tables[t].values["key"] = key;
    }

    context["typeclass"] = this.base_typeclass;
    context["key"] = key;

    service.saveObjectForm(tables,
                           this.base_typeclass,
                           this.obj_typeclass,
                           this.obj_key,
                           callback_success,
                           callback_failed,
                           context);
}

// Parse fields data to table headers.
ObjectEditor.prototype.propertiesFields = function(fields) {
    var cols = [{
        field: "operate",
        title: "Operate",
        formatter: this.propertiesButton,
    }];

    for (var i = 0; i < fields.length; i++) {
        cols.push({
            field: fields[i].name,
            title: fields[i].label,
            sortable: true,
        });
    }

    return cols;
}

// Set table buttons.
ObjectEditor.prototype.propertiesButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-level", row["level"])
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-level", row["level"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}
