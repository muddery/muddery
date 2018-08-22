
field_creator = {
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
        select_area.on("change", controller.onAreaChange);

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
}
