
/*
 * Derive from the base class.
 */
ElementEditor = function() {
	CommonEditor.call(this);

    this.base_element_type = "";
    this.obj_element_type = "";
    this.element_key = "";
    this.table_fields = [];

    this.event_fields = [];
    this.event_table = "event_data";

    this.properties_fields = [];
    this.properties_records = [];
    this.properties_table = "element_properties"
}

ElementEditor.prototype = prototype(CommonEditor.prototype);
ElementEditor.prototype.constructor = ElementEditor;

ElementEditor.prototype.init = function() {
    this.base_element_type = utils.getQueryString("base_element_type");
    this.obj_element_type = utils.getQueryString("element_type");
    this.element_key = utils.getQueryString("element_key");
    this.no_delete = utils.getQueryString("no_delete");

    if (sessionStorage.page_param) {
        this.field_values = JSON.parse(sessionStorage.page_param);
    }
    else {
        this.field_values = {};
    }

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.element_key && !this.no_delete) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.base_element_type);

    this.bindEvents();
    this.refresh();
}


/***********************************
 *
 * Events
 *
 ***********************************/
ElementEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.onAddEvent);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);

    $("#add-properties").on("click", this.onAddProperties);
    $("#properties-table").on("click", ".edit-row", this.onEditProperties);
    $("#properties-table").on("click", ".delete-row", this.onDeleteProperties);
}

ElementEditor.prototype.onImageLoad = function() {
    window.parent.controller.setFrameSize();
}

ElementEditor.prototype.onSave = function() {
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

ElementEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    service.deleteElement(
        controller.element_key,
        controller.base_element_type,
        controller.deleteSuccess,
        controller.failedCallback
    );
}

ElementEditor.prototype.onAddEvent = function(e) {
    if (!controller.element_key) {
        window.parent.controller.notify("You should save this element first.");
        return;
    }

    var editor = "element_event";
    var record = "";
    var args = {
        trigger: controller.element_key,
        element_type: controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
    }
    window.parent.controller.editRecord(editor, controller.event_table, record, true, args);
}

ElementEditor.prototype.onEditEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "element_event";
        var args = {
            trigger: controller.element_key,
            element_type: controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        }
        window.parent.controller.editRecord(editor, controller.event_table, record_id, true, args);
    }
}

ElementEditor.prototype.onDeleteEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteEvent,
                                     {record: record_id});
}

ElementEditor.prototype.confirmDeleteEvent = function(e) {
    window.parent.controller.hideWaiting();

    var record_id = parseInt(e.data.record);
    service.deleteRecord(controller.event_table, record_id, controller.deleteEventSuccess, controller.failedCallback);
}

ElementEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}

ElementEditor.prototype.onAddProperties = function(e) {
    if (!controller.element_key) {
        window.parent.controller.notify("You should save this element first.");
        return;
    }

    window.parent.controller.editElementProperties(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        null
    );
}

ElementEditor.prototype.onEditProperties = function(e) {
    var level = $(this).attr("data-level");
    window.parent.controller.editElementProperties(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        level
    );
}

ElementEditor.prototype.onDeleteProperties = function(e) {
    var level = $(this).attr("data-level");
    window.parent.controller.confirm(
        "",
        "Delete this level?",
        controller.confirmDeleteProperties,
        {level: level}
    );
}

ElementEditor.prototype.confirmDeleteProperties = function(e) {
    window.parent.controller.hideWaiting();

    var level = e.data.level;
    service.deleteElementLevelProperties(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        level,
        controller.deletePropertiesSuccess,
        controller.failedCallback
    );
}

ElementEditor.prototype.deletePropertiesSuccess = function(data) {
    var level = data.level;
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
ElementEditor.prototype.refresh = function() {
    // Query element form.
    service.queryElementForm(
        this.base_element_type,
        this.obj_element_type? this.obj_element_type: this.base_element_type,
        this.element_key,
        this.queryFormSuccess,
        this.failedCallback
    );
}

ElementEditor.prototype.uploadSuccess = function(field_name) {
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

ElementEditor.prototype.queryFormSuccess = function(data) {
    controller.table_fields = data;
    controller.obj_element_type = "";
    controller.element_key = "";

    // Get object's element type.
    for (var t = 0; t < data.length && !controller.obj_element_type; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "element_type") {
                var value = fields[f].value;
                if (value) {
                    controller.obj_element_type = value;
                }
                break;
            }
        }
    }

    // Get object's key.
    for (var t = 0; t < data.length && !controller.element_key; t++) {
        var fields = data[t].fields;
        for (var f = 0; f < fields.length; f++) {
            if (fields[f].name == "key") {
                var value = fields[f].value;
                if (value) {
                    controller.element_key = value;
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
    service.queryElementEventTriggers(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.queryEventTriggersSuccess,
        controller.failedCallback
    );

    service.queryElementEvents(
        controller.element_key,
        controller.queryEventTableSuccess,
        controller.failedCallback
    );

    // Query custom properties.
    service.queryElementProperties(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        controller.queryElementPropertiesSuccess,
        controller.failedCallback
    );
}

ElementEditor.prototype.queryEventTriggersSuccess = function(data) {
    // If can have events, show the events block.
    if (data && data.length > 0) {
        $("#events").show();
    }
    else {
        $("#events").hide();
    }
    window.parent.controller.setFrameSize();
}

ElementEditor.prototype.queryEventTableSuccess = function(data) {
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

ElementEditor.prototype.queryElementPropertiesSuccess = function(data) {
    controller.properties_fields = data.fields;
    controller.properties_records = data.records;

    if (!controller.properties_fields || controller.properties_fields.length == 0) {
        // If does not have custom properties.
        $("#properties").hide();
    }
    else {
        /*
        if (data.records.length > 1) {
            $("#show-properties-list")
                .attr("disabled", true)
                .attr("checked", true);
        }
        else {
            $("#show-properties-list")
                .attr("disabled", false)
                .attr("checked", false);
        }

        if （data.records.length <= 1) {
            // Show properties.

            if ($("#show-properties-levels").attr("checked")) {
                $("#properties-list").hide();
                $("#properties-levels").show();
            }
            else {
                $("#properties-levels").hide();
                $("#properties-list").show();
            }
        }
        else {
            $("#properties-list").hide();
            $("#properties-levels").show();
        }
        */

        $("#properties-list").hide();
        $("#properties-levels").show();

        // Set properties level table.
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
    }

    window.parent.controller.setFrameSize();
}

// Add form fields to the web page.
ElementEditor.prototype.setFields = function() {
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
                field.type = "HiddenInput";
            }

            var controller = this.createFieldController(field);
            if (controller) {
                controller.appendTo(block);
            }
        }
    }

    container.find(".control-item-element_type select").on("change", this.onElementTypeChanged);

    window.parent.controller.setFrameSize();
}

ElementEditor.prototype.onElementTypeChanged = function(e) {
    var element_type = this.value;

    if (controller.obj_element_type != element_type) {
        controller.obj_element_type = element_type;
        controller.refresh();
    }
}

ElementEditor.prototype.saveForm = function(callback_success, callback_failed, context) {
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
                else if (control.prop("tagName") == "SELECT") {
                    values[name] = control.val();
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

    context["element_type"] = this.base_element_type;
    context["key"] = key;

    service.saveElementForm(
        tables,
        this.base_element_type,
        this.obj_element_type? this.obj_element_type: this.base_element_type,
        this.element_key,
        callback_success,
        callback_failed,
        context
    );
}

// Parse fields data to table headers.
ElementEditor.prototype.propertiesFields = function(fields) {
    var cols = [];
    for (var i = 0; i < fields.length; i++) {
        cols.push({
            field: fields[i].name,
            title: fields[i].label,
            sortable: true,
        });
    }

    cols.push({
        field: "operate",
        title: "",
        formatter: this.propertiesButton,
    });

    return cols;
}

// Set table buttons.
ElementEditor.prototype.propertiesButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var level = row["level"];
    if (level === null) {
        level = "";
    }

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-level", level)
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-level", level)
        .text("Delete")
        .appendTo(block);

    return block.html();
}
