
controller = {
    init: function() {
        this.table_name = getQueryString("table");
        this.record_id = getQueryString("record");
        this.fields = [];

        this.bindEvents();

        $("#form-name").text(this.table_name);

        service.queryForm(this.table_name, this.record_id, this.queryFormSuccess);
    },

    bindEvents: function() {
    },

    queryFormSuccess: function(data) {
        controller.setFields(data);
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
            if (type == "CharField") {
                controller = this.createTextInput(label, name, value, help_text);
            }
            else if (type == "FloatField") {
                controller = this.createNumberInput(label, name, value, help_text);
            }
            else if (type == "TextField") {
                controller = this.createTextArea(label, name, value, help_text);
            }
            else if (type == "BooleanField") {
                if (value) {
                    if (value == "False" || value == "false") {
                        value = false;
                    }
                }
                controller = this.createCheckBox(label, name, value, help_text);
            }

            if (controller) {
                controller.appendTo(container);
            }
        }

        window.parent.controller.setFrameSize();
    },

    createControlGroup: function(controller, label, help_text) {
        var group = $("<div>")
            .addClass("control-group");

        // label
        var label_div = $("<label>")
            .addClass("control-label")
            .text(label)
            .appendTo(group);
        
        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        controller.appendTo(ctrl_div);

        $("<p>")
            .addClass("help-block")
            .text(help_text)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("message-block")
            .html("&nbsp;")
            .appendTo(ctrl_div);

        return group;
    },

    createTextInput: function(label, name, value, help_text) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "text")
            .attr("name", name)
            .val(value);
        
        return this.createControlGroup(controller, label, help_text);
    },

    createNumberInput: function(label, name, value, help_text) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "number")
            .attr("name", name)
            .val(value);

        return this.createControlGroup(controller, label, help_text);
    },

    createTextArea: function(label, name, value, help_text) {
        var controller = $("<textarea>")
            .addClass("form-control editor-control text-area-control")
            .attr("name", name)
            .attr("rows", "5")
            .val(value);
        
        return this.createControlGroup(controller, label, help_text);
    },

    createSelect: function(label, name, value, help_text, options) {
        var controller = $("<select>")
            .addClass("form-control editor-control select-control")
            .attr("name", name)
            .val(value);

        for (var i = 0; i < options.length; i++) {
            $("<option>")
                .text(options[i])
                .appendTo(controller);
        }
        
        return this.createControlGroup(controller, label, help_text);
    },

    createCheckBox: function(label, name, value, help_text, check) {
        var group = $("<div>")
            .addClass("control-group");

        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        var controller = $("<input>")
            .addClass("form-control editor-control check-box-control")
            .attr("type", "checkbox")
            .attr("name", name)
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
            .appendTo(ctrl_div);
        
        return group;
    },
}

$(document).ready(function() {
    controller.init();
});


