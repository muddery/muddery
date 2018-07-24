
controller = {
    areas: {},

    file_fields: [],

    init: function() {
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

        service.queryForm(this.table_name, this.record_id, this.queryFormSuccess);
    },

    bindEvents: function() {
        $("#exit-button").on("click", this.onExit);
        $("#save-record").on("click", this.onSave);
        $("#delete-record").on("click", this.onDelete);
    },

    onExit: function() {
        controller.exit_no_change();
    },

    onSave: function() {
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
    },

    uploadSuccess: function(field_name) {
        var callback = function(data) {
            for (var i = 0; i < controller.file_fields.length; i++) {
                if (controller.file_fields[i] == field_name) {
                    controller.file_fields.splice(i, 1);
                    var field = $("#control-" + field_name);
                    field.find(".editor-control").val(data.resource);
                    field.find("img").attr("src", CONFIG.resource_url + data.resource);
                    break;
                }
            }

            if (controller.file_fields.length == 0) {
                controller.saveFields();
            }
        }

        return callback;
    },

    uploadFailed: function(code, message, data) {
        window.parent.controller.notify("ERROR", code + ": " + message);
    },

    onDelete: function() {
        window.parent.controller.confirm("",
                                         "Delete this record?",
                                         controller.confirmDelete);
    },

    onAreaChange: function(e) {
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
    },

    queryFormSuccess: function(data) {
        if (data.hasOwnProperty("areas")) {
            controller.areas = data.areas;
        }
        controller.setFields(data.fields);

        if (data.hasOwnProperty("events")) {
            controller.setEvents(data.events);
        }
    },

    setFields: function(fields) {
        this.fields = fields;

        var container = $("#fields");
        for (var i = 0; i < fields.length; i++) {
            var type = fields[i].type;
            var label = fields[i].label;
            var name = fields[i].name;
            var help_text = fields[i].help_text;
            var value = fields[i].value;

            var controller;
            if (type == "Location") {
                controller = this.createAreaSelect(name, label, value, help_text, this.areas);
            }
            else if (type == "Image") {
                controller = this.createImageInput(fields[i].image_type, name, label, value, help_text);
            }
            else if (type == "Hidden") {
                controller = this.createHiddenInput(name, label, value, help_text);
            }
            else if (type == "TextInput") {
                controller = this.createTextInput(name, label, value, help_text);
            }
            else if (type == "NumberInput") {
                controller = this.createNumberInput(name, label, value, help_text);
            }
            else if (type == "Textarea") {
                controller = this.createTextArea(name, label, value, help_text);
            }
            else if (type == "CheckboxInput") {
                if (value) {
                    if (value == "False" || value == "false") {
                        value = false;
                    }
                }
                controller = this.createCheckBox(name, label, value, help_text);
            }
            else if (type == "Select") {
                controller = this.createSelect(name, label, value, help_text, fields[i].choices);
            }

            if (controller) {
                controller.appendTo(container);
            }
        }

        window.parent.controller.setFrameSize();
    },

    createControlGroup: function(name, ctrl, label, help_text) {
        var group = $("<div>")
            .addClass("control-group")
            .attr("id", "control-" + name);

        // label
        var label_div = $("<label>")
            .addClass("control-label")
            .text(label)
            .appendTo(group);
        
        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        ctrl.appendTo(ctrl_div);

        $("<p>")
            .addClass("help-block")
            .text(help_text)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("message-block")
            .hide()
            .appendTo(ctrl_div);

        return group;
    },

    createHiddenInput: function(name, label, value, help_text) {
        var group = $("<div>")
            .addClass("control-group hidden")
            .attr("id", "control-" + name);

        var controller = $("<input>")
            .addClass("editor-control")
            .attr("type", "hidden")
            .val(value)
            .appendTo(group);

        return group;
    },

    createTextInput: function(name, label, value, help_text) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "text")
            .val(value);
        
        return this.createControlGroup(name, controller, label, help_text);
    },

    createNumberInput: function(name, label, value, help_text) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "number")
            .val(value);

        return this.createControlGroup(name, controller, label, help_text);
    },

    createTextArea: function(name, label, value, help_text) {
        var controller = $("<textarea>")
            .addClass("form-control editor-control text-area-control")
            .attr("rows", "5")
            .val(value);
        
        return this.createControlGroup(name, controller, label, help_text);
    },

    createSelect: function(name, label, value, help_text, options) {
        var controller = $("<select>")
            .addClass("form-control editor-control select-control")
            .val(value);

        for (var i = 0; i < options.length; i++) {
            var option = $("<option>")
                .text(options[i][1])
                .attr("value", options[i][0])
                .appendTo(controller);

            if (options[i][0] == value) {
                option.attr("selected", "selected");
            }
        }
        
        return this.createControlGroup(name, controller, label, help_text);
    },

    createCheckBox: function(name, label, value, help_text, check) {
        var group = $("<div>")
            .addClass("control-group")
            .attr("id", "control-" + name);

        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        var controller = $("<input>")
            .addClass("form-control editor-control check-box-control")
            .attr("type", "checkbox")
            .appendTo(ctrl_div);

        if (value) {
            controller.attr("checked", "checked");
        }

        // label
        var label_div = $("<label>")
            .addClass("control-label")
            .text(label)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("help-block")
            .text(help_text)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("message-block")
            .html("&nbsp;")
            .hide()
            .appendTo(ctrl_div);
        
        return group;
    },

    createAreaSelect: function(name, label, value, help_text, areas) {
        var ctrl = $("<div>");

        // Add area.
        var select_area = $("<select>")
            .addClass("select-area form-control select-control");

        var selected_area = "";
        var first_area = "";
        for (var key in areas) {
            if (!first_area) {
                first_area = key;
            }
            var area = areas[key];

            var option = $("<option>")
                .text(area.name)
                .attr("value", key)
                .appendTo(select_area);

            if (!selected_area) {
                for (var r = 0; r < area.rooms.length; r++) {
                    if (area.rooms[r][0] == value) {
                        option.attr("selected", "selected");
                        selected_area = key;
                        break;
                    }
                }
            }
        }
        select_area.appendTo(ctrl);
        select_area.on("change", this.onAreaChange);

        if (!selected_area) {
            selected_area = first_area;
        }

        // Add room.
        var select_room = $("<select>")
            .addClass("select-room form-control editor-control select-control");

        var room_area = areas[selected_area];
        for (var i = 0; i < room_area.rooms.length; i++) {
            var room = room_area.rooms[i];

            var option = $("<option>")
                .text(room[1])
                .attr("value", room[0])
                .appendTo(select_room);

            if (room[0] == value) {
                option.attr("selected", "selected");
            }
        }
        select_room.appendTo(ctrl);
        
        return this.createControlGroup(name, ctrl, label, help_text);
    },

    createImageInput: function(image_type, name, label, value, help_text) {
        var ctrl = $("<div>");

        var image = $("<img>")
            .addClass("image-" + image_type)
            .attr("id", "image-" + name)
            .appendTo(ctrl);

        var input = $("<input>")
            .addClass("form-control image-input-control")
            .attr("type", "file")
            .data("image_type", image_type)
            .data("field_name", name)
            .appendTo(ctrl);

        var resource = $("<input>")
            .addClass("editor-control")
            .attr("type", "hidden")
            .appendTo(ctrl);

        if (value) {
            image.attr("src", CONFIG.resource_url + value);
            resource.val(value);
        }

        return this.createControlGroup(name, ctrl, label, help_text);
    },

    setEvents: function(events) {
    },

    exit: function() {
        window.parent.controller.showTable(this.table_name);
    },

    exit_no_change: function() {
        window.parent.controller.showTableView();
    },

    saveFields: function() {
        var values = {};
        for (var i = 0; i < this.fields.length; i++) {
            var name = this.fields[i].name;
            var control = $("#control-" + name + " .editor-control");
            if (control.length > 0) {
                if (control.attr("type") == "checkbox") {
                    values[name] = control.prop("checked");
                }
                else {
                    values[name] = control.val();
                }
            }
        }

        service.saveForm(values, 
                         this.table_name,
                         this.record_id,
                         this.saveFormSuccess,
                         this.saveFormFailed);
    },

    saveFormSuccess: function(data) {
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
    },

    saveFormFailed: function(code, message, data) {
        if (code == 10006) {    // invalid form
            $("#form-message")
                .text("Invalid input.")
                .addClass("message-error")
                .removeClass("message-success")
                .removeClass("hidden")
                .show();

            $(".message-block")
                .hide();

            for (var name in data) {
                $("#control-" + name + " .message-block")
                    .text(data[name])
                    .show();
            }
        }
    },

    confirmDelete: function(e) {
        window.parent.controller.hide_waiting();

        service.deleteRecord(controller.table_name,
                             controller.record_id,
                             controller.deleteSuccess);
    },

    deleteSuccess: function(data) {
        controller.exit();
    },
}

$(document).ready(function() {
    controller.init();
});


