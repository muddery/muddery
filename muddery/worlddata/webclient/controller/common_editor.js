
/*
 * Get the prototype of the base class.
 */
prototype = function(base, el) {
    var Base = function(){};
    Base.prototype = base;
    return new Base(el);
}


////////////////////////////////////////
//
// The base of view controllers.
//
////////////////////////////////////////

/*
 * The base controller's constructor.
 */
CommonEditor = function() {
    this.table_name = "";
    this.record_id = "";
    this.fields = [];
    this.areas = {};
    this.file_fields = [];
}

CommonEditor.prototype.init = function() {
    this.table_name = utils.getQueryString("table");
    this.record_id = utils.getQueryString("record");

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.record_id) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.table_name);

    this.bindEvents();
    this.refresh();
}

CommonEditor.prototype.bindEvents = function() {
    $("#exit-button").on("click", this.onExit);
    $("#save-record").on("click", this.onSave);
    $("#delete-record").on("click", this.onDelete);
}

CommonEditor.prototype.onExit = function() {
    controller.exitNoChange();
}

CommonEditor.prototype.onSave = function() {
    controller.saveFields(controller.saveFormSuccess, controller.saveFormFailed);
}

CommonEditor.prototype.onDelete = function() {
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete);
}

CommonEditor.prototype.onAreaChange = function(e) {
    var area_key = this.value;
    var room_area = controller.areas[area_key];
    var select_room = $(this).parent().find(".select-room");
    select_room.find("option").remove();

    for (var i = 0; i < room_area.rooms.length; i++) {
        var room = room_area.rooms[i];

        var option = $("<option>")
            .text(room[1])
            .attr("value", room[0])
            .appendTo(select_room);
    }
}

CommonEditor.prototype.refresh = function() {
    service.queryForm(this.table_name, this.record_id, this.queryFormSuccess, this.queryFormFailed);
}

CommonEditor.prototype.queryFormSuccess = function(data) {
    controller.fields = data;

    // If has area fields.
    var query_areas = false;
    for (var i = 0; i < data.length; i++) {
        if (data[i].type == "Location") {
            query_areas = true;
            break;
        }
    }

    if (query_areas) {
        service.queryAreas(controller.queryAreasSuccess, controller.queryAreasFailed);
    }
    else {
        controller.queryAreasSuccess({});
    }
}

CommonEditor.prototype.queryFormFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

CommonEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();
}

CommonEditor.prototype.queryAreasFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

// Add form fields to the web page.
CommonEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var controller = this.createFieldController(this.fields[i]);
        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}

CommonEditor.prototype.createFieldController = function(field) {
    var type = field.type;
    var label = field.label;
    var name = field.name;
    var help_text = field.help_text;
    var value = field.value;

    var controller = null;
    if (type == "Location") {
        controller = field_creator.createAreaSelect(name, label, value, help_text, this.areas);
    }
    else if (type == "Image") {
        controller = field_creator.createImageInput(field.image_type, name, label, value, help_text);
    }
    else if (type == "Hidden") {
        controller = field_creator.createHiddenInput(name, label, value, help_text);
    }
    else if (type == "TextInput") {
        controller = field_creator.createTextInput(name, label, value, help_text);
    }
    else if (type == "NumberInput") {
        controller = field_creator.createNumberInput(name, label, value, help_text);
    }
    else if (type == "Textarea") {
        controller = field_creator.createTextArea(name, label, value, help_text);
    }
    else if (type == "CheckboxInput") {
        if (value) {
            if (value == "False" || value == "false") {
                value = false;
            }
        }
        controller = field_creator.createCheckBox(name, label, value, help_text);
    }
    else if (type == "Select") {
        controller = field_creator.createSelect(name, label, value, help_text, field.choices);
    }

    return controller;
}

CommonEditor.prototype.exit = function() {
    window.parent.controller.popPage(true);
}

CommonEditor.prototype.exitNoChange = function() {
    window.parent.controller.popPage(false);
}

CommonEditor.prototype.saveFields = function(callback_success, callback_failed, context) {
    var values = {};
    for (var i = 0; i < this.fields.length; i++) {
        var name = this.fields[i].name;
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

    service.saveForm(values,
                     this.table_name,
                     this.record_id,
                     callback_success,
                     callback_failed,
                     context);
}

CommonEditor.prototype.saveFormSuccess = function(data) {
    /*
    $("#form-message")
        .text("Save success.")
        .addClass("message-success")
        .removeClass("message-error")
        .removeClass("hidden")
        .show();

    $(".message-block")
        .hide();
    */

    controller.exit();
}

CommonEditor.prototype.saveFormFailed = function(code, message, data) {
    // Hide current messages.
    $(".message-block")
        .hide();

    var text = "Error: [" + code + "] " + message;

    if (code == 10006) {
        // Invalid form
        if (typeof(data) == "object") {
            for (var name in data) {
                // Set return messages.
                var field = $("#control-" + name + " .message-block");
                if (field.length > 0) {
                    field
                        .text(data[name])
                        .show();
                }
                else {
                    text += " " + data[name];
                }
            }
        }
        else {
            text += " " + data;
        }
    }

    $("#form-message")
        .text(text)
        .addClass("message-error")
        .removeClass("message-success")
        .removeClass("hidden")
        .show();
}

CommonEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    service.deleteRecord(controller.table_name,
                         controller.record_id,
                         controller.deleteSuccess);
}

CommonEditor.prototype.deleteSuccess = function(data) {
    controller.exit();
}

// Parse fields data to table headers.
CommonEditor.prototype.parseFields = function(fields) {
    var cols = [{
        field: "operate",
        title: "Operate",
        formatter: this.operateButton,
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
CommonEditor.prototype.operateButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-record-id", row["id"])
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-record-id", row["id"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}
