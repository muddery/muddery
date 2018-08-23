
/*
 * Derive from the base class.
 */
EventEditor = function() {
	CommonEditor.call(this);

    this.trigger_obj = "";
}

EventEditor.prototype = prototype(CommonEditor.prototype);
EventEditor.prototype.constructor = EventEditor;

EventEditor.prototype.init = function() {
    this.table_name = getQueryString("table");
    this.record_id = getQueryString("record");
    this.trigger_obj = getQueryString("trigger");
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

EventEditor.prototype.setFields = function(fields) {
    this.fields = fields;

    var container = $("#fields");
    for (var i = 0; i < fields.length; i++) {
        var type = fields[i].type;
        var label = fields[i].label;
        var name = fields[i].name;
        var help_text = fields[i].help_text;
        var value = fields[i].value;

        // Users can not set the event's key and trigger object.
        if (name == "key") {
            type = "Hidden";
        }
        else if (name == "trigger_obj") {
            type = "Hidden";
            value = this.trigger_obj;
        }

        var controller;
        if (type == "Location") {
            controller = field_creator.createAreaSelect(name, label, value, help_text, this.areas);
        }
        else if (type == "Image") {
            controller = field_creator.createImageInput(fields[i].image_type, name, label, value, help_text);
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
            controller = field_creator.createSelect(name, label, value, help_text, fields[i].choices);
        }

        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}
