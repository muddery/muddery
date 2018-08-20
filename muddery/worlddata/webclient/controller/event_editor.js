
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
        controller.saveFields();
    },

    onDelete: function() {
        window.parent.controller.confirm("",
                                         "Delete this record?",
                                         controller.confirmDelete);
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
                controller = fields.createAreaSelect(name, label, value, help_text, this.areas);
            }
            else if (type == "Image") {
                controller = fields.createImageInput(fields[i].image_type, name, label, value, help_text);
            }
            else if (type == "Hidden") {
                controller = fields.createHiddenInput(name, label, value, help_text);
            }
            else if (type == "TextInput") {
                controller = fields.createTextInput(name, label, value, help_text);
            }
            else if (type == "NumberInput") {
                controller = fields.createNumberInput(name, label, value, help_text);
            }
            else if (type == "Textarea") {
                controller = fields.createTextArea(name, label, value, help_text);
            }
            else if (type == "CheckboxInput") {
                if (value) {
                    if (value == "False" || value == "false") {
                        value = false;
                    }
                }
                controller = fields.createCheckBox(name, label, value, help_text);
            }
            else if (type == "Select") {
                controller = fields.createSelect(name, label, value, help_text, fields[i].choices);
            }

            if (controller) {
                controller.appendTo(container);
            }
        }

        window.parent.controller.setFrameSize();
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


